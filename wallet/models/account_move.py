# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from collections import defaultdict

import logging

_logger = logging.getLogger(__name__)


def sort_by_wallet_hierarchy(line_tuple):
    wallet_id = line_tuple[0]
    parent_count = wallet_id.category_id.parent_count
    if wallet_id != wallet_id.get_default_wallet():
        parent_count += 1
    return parent_count


class AccountMove(models.Model):
    _inherit = 'account.move'

    def is_wallet_payment(self):
        self.ensure_one()
        product_ids = self.mapped("invoice_line_ids").mapped("product_id")
        for product_id in product_ids:
            if product_id in self.env["wallet.category"].search([]).mapped("product_id"):
                return True
        return False

    def get_wallet_paid_amounts(self):
        self.ensure_one()
        wallet_amount_to_apply = defaultdict(float)
        default_wallet = self.env.ref("wallet.default_wallet_category")
        for reconcile_json in self._get_reconciled_info_JSON_values():
            reconcile_move_id = self.env["account.move"].browse([reconcile_json["move_id"]])
            if reconcile_json["account_payment_id"] or not reconcile_move_id.is_wallet_payment():
                wallet_amount_to_apply[default_wallet] += reconcile_json["amount"]
            else:
                move_invoice_line_ids = reconcile_move_id.mapped("invoice_line_ids")
                if move_invoice_line_ids:
                    for wallet_id, amount in move_invoice_line_ids.mapped(lambda line: (
                            self.env["wallet.category"].search([("product_id", "=", line.product_id.id)]),
                            line.price_total)):
                        wallet_amount_to_apply[wallet_id] += amount
        return dict(wallet_amount_to_apply)

    def get_wallet_raw_due_amounts(self):
        self.ensure_one()
        invoice_line_ids = self.mapped("invoice_line_ids")
        tuple_list_category_amount = invoice_line_ids.mapped(
            lambda invoice_line_id: (self.env["wallet.category"].
                                     get_wallet_by_category_id(invoice_line_id.product_id.categ_id),
                                     invoice_line_id.price_total))
        current_invoices_category_amounts = defaultdict(float)
        for category_id, amount in tuple_list_category_amount:
            current_invoices_category_amounts[category_id] += amount
        return dict(current_invoices_category_amounts)

    def get_wallet_due_amounts(self):
        walletCategoryEnv = self.env["wallet.category"]

        all_wallet_due_amounts = defaultdict(float)
        for move_id in self:
            # Getting the due amount without payments
            wallet_raw_due_amounts = move_id.get_wallet_raw_due_amounts()
            wallet_due_amounts = dict(wallet_raw_due_amounts)

            # Getting how much has been paid with wallets
            wallet_paid_amounts = defaultdict(float, move_id.get_wallet_paid_amounts())
            if wallet_paid_amounts:
                # Sorting them by wallet hierarchy, this part is crucial
                sorted_wallet_raw_due_amounts = sorted(wallet_raw_due_amounts.items(), key=sort_by_wallet_hierarchy,
                                                       reverse=True)

                for wallet_id, amount in sorted_wallet_raw_due_amounts:
                    looking_wallet = wallet_id
                    while amount > 0:
                        looking_wallet_amount = wallet_paid_amounts[looking_wallet]
                        if looking_wallet_amount > 0:
                            wallet_remove_amount = amount

                            if looking_wallet_amount - amount < 0:
                                wallet_remove_amount = looking_wallet_amount

                            wallet_paid_amounts[looking_wallet] = round(round(wallet_paid_amounts[looking_wallet], 2) \
                                                                    - \
                                                                    round(wallet_remove_amount, 2), 2)
                            amount = round(round(amount, 2) - round(wallet_remove_amount, 2), 2)
                            wallet_due_amounts[wallet_id] = round(round(wallet_due_amounts[wallet_id], 2) - round(wallet_remove_amount, 2), 2)
                        if looking_wallet == self.env.ref("wallet.default_wallet_category"):
                            break
                        looking_wallet = wallet_id.get_wallet_by_category_id(looking_wallet.category_id.parent_id)

            for wallet_id, amount in wallet_due_amounts.items():
                all_wallet_due_amounts[wallet_id] = round(round(all_wallet_due_amounts[wallet_id], 2) + round(amount, 2), 2)

        return all_wallet_due_amounts

    def pay_with_wallet(self, wallet_payment_dict):
        """
        wallet_payment_dict: should be a dict with the form {wallet_id: amount,...}
        this method only work for invoices that has the same partner_id.

        this method order automatically per date

        TODO: Be able to do move_ids.pay_with_wallet(wallet_payment_dict) where those move_ids has different customers
        """
        if wallet_payment_dict:

            move_ids = self.sorted("invoice_date_due")
            accountMoveEnv = self.env["account.move"]
            journal_ids = set(map(lambda wallet_id: wallet_id.journal_category_id, wallet_payment_dict.keys()))

            partner_id = move_ids.mapped("partner_id").ensure_one()
            for move_id in move_ids:
                total_to_pay = move_id.calculate_wallet_distribution(move_id.get_wallet_due_amounts(),
                                                                     wallet_payment_dict)

                if total_to_pay:
                    for journal_id in journal_ids:
                        filtered_wallet_line_ids = {wallet_id: amount
                                                    for wallet_id, amount in total_to_pay.items()
                                                    if wallet_id.journal_category_id == journal_id}

                        if filtered_wallet_line_ids:

                            invoice_line_ids = []
                            for wallet_id, amount in filtered_wallet_line_ids.items():

                                # We check if there is available wallet
                                wallet_amount = wallet_id.get_wallet_amount(partner_id)
                                if wallet_amount > -abs(wallet_id.credit_limit):

                                    invoice_line_ids.append((0, 0, {
                                        "product_id": wallet_id.product_id.id,
                                        # "account_id": wallet_id.account_id.id,
                                        "price_unit": amount,
                                        "quantity": 1,
                                    }))
                                else:
                                    raise exceptions.ValidationError(_("Your are trying to pay %s in %s when there is only %s available") % (amount, wallet_id.name, wallet_amount))

                            credit_note_id = accountMoveEnv.create({
                                "type": "out_refund",
                                "partner_id": partner_id,
                                "journal_id": journal_id.id,
                                "invoice_line_ids": invoice_line_ids,
                            })

                            # We need to ensure that the credit note has the same receivable than the invoice
                            # So we force it
                            move_receivable_line_id = move_id.line_ids. \
                                filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')

                            receivable_line_id = credit_note_id.line_ids. \
                                filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')

                            receivable_line_id.account_id = move_receivable_line_id.account_id

                            credit_note_id.post()
                            _logger.info("Invoice [%s]: %s paid to %s with: credit note [%s]: %s, amount: %s" %
                                         (move_id.id, move_id.name, partner_id,
                                          credit_note_id.id, credit_note_id.name, credit_note_id.amount_total))
                            move_id.js_assign_outstanding_line(receivable_line_id.id)

            wallet_ids = self.env["wallet.category"].browse(set(map(lambda wallet_id: wallet_id.id, wallet_payment_dict.keys())))
            wallet_ids.sorted("category_id.parent_count", reverse=True)
            for wallet_id in wallet_ids:
                wallet_amount = wallet_id.get_wallet_amount(partner_id)
                if wallet_amount < wallet_id.credit_limit:
                    raise exceptions.ValidationError(_("[%s] Wallet will have a final amount of [%s]!. Credit limit: %s") % (wallet_id.name, wallet_amount, wallet_id.credit_limit))

    def get_available_wallet_amounts(self):
        """ This will return an array of dicts
            [
                "partner_1": {wallet_things},
                "partner_2": {wallet_things2},
            ]
         """
        partner_ids_wallet_amounts = {}
        if self:
            partner_ids = self.mapped("partner_id")
            walletCategoryEnv = self.env["wallet.category"]
            for partner_id in partner_ids:
                move_ids = self.filtered(lambda move: move.partner_id == partner_id).sorted("invoice_date_due")
                walletCategoryEnv = self.env["wallet.category"]

                # Getting how much we can pay
                all_wallet_ids = walletCategoryEnv.search([])
                partner_wallet_amounts = {wallet_id: wallet_id.get_wallet_amount(partner_id)
                                          for wallet_id in all_wallet_ids}

                # Now we perform the operations
                wallet_to_apply = defaultdict(float)
                for move_id in move_ids:
                    move_wallet_amounts = move_id.get_wallet_due_amounts()
                    total_to_pay = self.calculate_wallet_distribution(move_wallet_amounts, partner_wallet_amounts)
                    for wallet_id, amount in total_to_pay.items():
                        wallet_to_apply[wallet_id] += amount

                # wallet_to_apply = self.calculate_wallet_distribution(current_invoices_category_amounts,
                # partner_wallet_amounts)
                partner_ids_wallet_amounts.update({partner_id: dict(wallet_to_apply)})
        return partner_ids_wallet_amounts

    def calculate_wallet_distribution(self, wallet_dict_to_pay, wallet_dict_available):
        #wallet_dict_available = defaultdict(float, wallet_dict_available)
        sorted_wallet_dict_to_pay = sorted(wallet_dict_to_pay.items(), key=sort_by_wallet_hierarchy, reverse=True)
        wallet_amount_to_apply = defaultdict(float)
        for wallet_id, amount in sorted_wallet_dict_to_pay:
            looking_wallet = wallet_id
            while amount > 0:
                if looking_wallet in wallet_dict_available:
                    looking_wallet_amount = wallet_dict_available[looking_wallet]
                    if looking_wallet_amount > -abs(wallet_id.credit_limit):
                        wallet_remove_amount = amount

                        if looking_wallet_amount - amount < -abs(looking_wallet.credit_limit):
                            wallet_remove_amount = looking_wallet_amount + abs(looking_wallet.credit_limit)

                        wallet_dict_available[looking_wallet] = round(wallet_dict_available[looking_wallet], 2) \
                                                                - \
                                                                round(wallet_remove_amount, 2)
                        amount = round(amount, 2) - round(wallet_remove_amount, 2)

                        wallet_amount_to_apply[looking_wallet] = round(wallet_amount_to_apply[looking_wallet], 2) + round(
                            wallet_remove_amount, 2)
                if looking_wallet == self.env.ref("wallet.default_wallet_category"):
                    break
                looking_wallet = wallet_id.get_wallet_by_category_id(looking_wallet.category_id.parent_id)
        return dict(wallet_amount_to_apply)
