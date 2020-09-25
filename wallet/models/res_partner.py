# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import ValidationError
import json
import typing

logger = logging.getLogger(__name__)


def sort_by_wallet_hierarchy(line_tuple):
    wallet_id = line_tuple[0]
    parent_count = wallet_id.category_id.parent_count
    if wallet_id != wallet_id.get_default_wallet():
        parent_count += 1
    return parent_count


def sort_invoice_line_by_wallet_hierarchy(invoice_line_id):
    wallet_id = invoice_line_id.env["wallet.category"].get_wallet_by_category_id(invoice_line_id.product_id.categ_id)
    parent_count = wallet_id.category_id.parent_count
    if wallet_id != wallet_id.get_default_wallet():
        parent_count += 1
    return parent_count


class ResPartner(models.Model):
    _inherit = 'res.partner'

    json_dict_wallet_amounts = fields.Char(compute="_compute_json_dict_wallet_amounts")
    total_wallet_balance = fields.Monetary(string="Total Wallet Balance",
        compute="_compute_total_wallet_balance")

    def execute_autoclear(self):
        for partner in self:
            try:
                if partner.id == 3356:
                    debug = 0
                partner.autoload_payments_to_wallet()
                partner.autoload_credit_notes_to_wallet()
                partner.autopay_invoices_with_wallet()
            except Exception as err:
                raise err

    def autoload_credit_notes_to_wallet(self):
        for partner_id in self:
            partner_credit_note_ids = partner_id.get_unreconciled_credit_notes()
            if partner_credit_note_ids:
                credit_note_wallets_due = partner_credit_note_ids.get_wallet_due_amounts()
                sorted_credit_note_wallet_dues = sorted(credit_note_wallets_due.items(), key=sort_by_wallet_hierarchy,
                                                        reverse=True)

                for wallet_id, amount in sorted_credit_note_wallet_dues:
                    partner_id.load_wallet_with_credit_notes(partner_credit_note_ids, wallet_id, amount)

    def get_unreconciled_credit_notes(self):
        self.ensure_one()
        credit_note_ids = self.env["account.move"].search(
            [
                ("partner_id", "=", self.id),
                ("invoice_payment_state", "!=", "paid"),
                ("state", "=", "posted"),

                # out_refund = Credit note
                ("type", "=", "out_refund"),
            ]
        )
        return credit_note_ids

    def autopay_invoices_with_wallet(self):
        # Yes, I KNOW THAT I CAN USE INVOICE_IDS! But, in the future, we are going to make
        # the domain more complex and even with invoices that haven't their partner as customer
        for partner_id in self:
            move_ids = self.env["account.move"].search(
                [
                    ("partner_id", "=", partner_id.id),
                    ("invoice_payment_state", "!=", "paid"),
                    ("state", "=", "posted"),
                    ("type", "=", "out_invoice"),
                ]
            )
            move_ids_wallet_amounts = move_ids.get_available_wallet_amounts()
            if move_ids_wallet_amounts:
                partner_wallet_amounts = move_ids_wallet_amounts[partner_id]
                move_ids.pay_with_wallet(partner_wallet_amounts)

    def autoload_payments_to_wallet(self):
        """ This will load payment to wallet automatically """
        for record in self:
            wallet_ids = self.env["wallet.category"].search([])
            payment_grouped = {}
            default_wallet_id = self.env.ref("wallet.default_wallet_category")

            # We find and group payment with wallets
            for wallet_id in wallet_ids:
                domain_payment_wallet_id = wallet_id.id
                if wallet_id == default_wallet_id:
                    domain_payment_wallet_id = False
                payment_ids = self.env["account.payment"].search(
                    [
                        ("partner_id", "=", self.id),
                        ("unpaid_amount", ">", 0),
                        ("wallet_id", "=", domain_payment_wallet_id),
                        ("state", "in", ["posted", "sent", "reconciled"]),
                    ]
                )
                if payment_ids:
                    payment_grouped[wallet_id] = payment_ids

            # We start load wallet to partners
            for wallet_id, payment_ids in payment_grouped.items():
                amount = sum(payment_ids.mapped("unpaid_amount"))
                record.load_wallet_with_payments(payment_ids, wallet_id, amount)
                logger.info("Wallet loaded to %s with: wallet_id: %s, payment_ids: %s, amount: %s" % (record,
                                                                                                      wallet_id,
                                                                                                      payment_ids,
                                                                                                      amount))

    def load_wallet_with_credit_notes(self, credit_note_ids, wallet_id, amount):
        """
        Load the wallet with credit notes, please, be sure that the amount is correctly
        :param credit_note_ids: credit notes that will pay the wallet
        :param wallet_id: the wallet to load
        :param amount: how much will be loaded.
        :return: the moves created to load wallet
        """
        self.ensure_one()
        move_ids = self.env["account.move"]
        wallet_env = self.env["wallet.category"]
        credit_note_ids = credit_note_ids.filtered(lambda credit_note: credit_note.invoice_payment_state != 'paid')

        credit_note_wallet_amounts_list = []
        for credit_note_id in credit_note_ids:
            credit_note_wallet_amounts = credit_note_id.get_wallet_due_amounts().items()
            for wallet, wallet_amount in credit_note_wallet_amounts:
                credit_note_wallet_amounts_list.append((credit_note_id, wallet, wallet_amount))

        def sort_credit_note_wallet_amounts_list(credit_note_tuple):
            """ Used for sorting the by wallet hierarchy """
            wallet_id = credit_note_tuple[1]
            parent_count = wallet_id.category_id.parent_count
            if wallet_id != wallet_id.get_default_wallet():
                parent_count += 1
            return parent_count

        sorted_credit_note_wallet_amounts_list = sorted(credit_note_wallet_amounts_list,
                                                        key=sort_credit_note_wallet_amounts_list,
                                                        reverse=True)
        for credit_note_id, credit_note_wallet_id, credit_note_wallet_amount in sorted_credit_note_wallet_amounts_list:

            if amount <= 0:
                break

            credit_note_amount_to_pay = credit_note_wallet_amount if credit_note_wallet_amount < amount else amount

            if credit_note_amount_to_pay:
                company_id = self.company_id or self.env.user.company_id

                move_id = self.env["account.move"].create({
                    "type": "out_invoice",
                    "partner_id": self.id,
                    "journal_id": wallet_id.journal_category_id.id,
                    "invoice_line_ids": [(0, 0, {
                        "product_id": wallet_id.product_id.id,
                        "price_unit": credit_note_amount_to_pay,
                        "quantity": 1,
                    })],
                    "company_id": company_id.id
                })

                move_id.post()
                move_receivable_line_id = move_id.line_ids. \
                    filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')

                credit_note_receivable_line_id = credit_note_id.line_ids. \
                    filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')

                move_receivable_line_id.account_id = credit_note_receivable_line_id.account_id

                for receivable_line_id in credit_note_receivable_line_id:
                    move_id.js_assign_outstanding_line(receivable_line_id.id)

                # We do round(round(amount, 2) - round(credit_note_amounts, 2), 2)
                # to avoid 0.1 + 0.2 = 0.30000000000000004
                amount = round(round(amount, 2) - round(credit_note_amount_to_pay, 2), 2)
                move_ids += move_id

        return move_ids

    def load_wallet_with_payments(self, payment_ids, wallet_id, amount):
        self.ensure_one()

        if type(payment_ids) == list:
            payment_ids = self.env["account.payment"].browse(payment_ids)

        accountMoveEnv = self.env["account.move"]
        move_ids = self.env["account.move"]

        company_id = self.company_id or self.env.user.company_id
        move_id = accountMoveEnv.create({
            "type": "out_invoice",
            "partner_id": self.id,
            "journal_id": wallet_id.journal_category_id.id,
            "invoice_line_ids": [(0, 0, {
                "product_id": wallet_id.product_id.id,
                "price_unit": amount,
                "quantity": 1,
            })],
            "company_id": company_id.id
        })

        move_id.post()

        payments_receivable_line_ids = payment_ids.move_line_ids.filtered(
            lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')

        for receivable_line_id in payments_receivable_line_ids:
            move_id.js_assign_outstanding_line(receivable_line_id.id)

        move_ids += move_id

        return move_ids
    
    def _compute_total_wallet_balance(self):
        for partner in self:
            result = 0
            for key, value in partner.get_wallet_balances_dict([]).items():
                result += value
            partner.total_wallet_balance = result

    def _compute_json_dict_wallet_amounts(self):
        for partner_id in self:
            partner_id.json_dict_wallet_amounts = partner_id.get_wallet_balances_json([])

    def get_wallet_balances_json(self, wallet_id_list: typing.List[int]) -> str:
        """ :return A json with the wallet balances """

        self.ensure_one()
        return json.dumps(self.get_wallet_balances_dict(wallet_id_list))

    def get_wallet_balances_dict(self, wallet_id_list: typing.List[int]) -> dict:
        """ :return A dict with the wallet balances """

        self.ensure_one()
        wallet_category_ids = self.env["wallet.category"]
        if wallet_id_list:
            wallet_category_ids = wallet_category_ids.browse(wallet_id_list)
        else:
            wallet_category_ids = wallet_category_ids.search([])
        dict_wallet_amounts = {}
        for wallet_category_id in wallet_category_ids:
            dict_wallet_amounts[wallet_category_id.id] = wallet_category_id.get_wallet_amount(self)
        return dict_wallet_amounts

    def action_open_wallet_history(self):
        self.ensure_one()
        action = self.env.ref("wallet.account_move_line_action_wallet_history").read()[0]
        wallets = self.env["wallet.category"].search([])
        products = wallets.mapped("product_id")
        action["domain"] = [("partner_id","=",self.id),("product_id","in",products.ids)]
        return action