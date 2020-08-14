# -*- coding: utf-8 -*-

from odoo import models, fields, api


# noinspection PyProtectedMember
class InvoicePaymentRegister(models.Model):
    """ This model will save payments to invoices
        So we can use it for pay them when the session
        is closed """

    _name = 'pos_pr.invoice.payment'

    name = fields.Char()
    date = fields.Date()

    payment_amount = fields.Float()
    payment_method_id = fields.Many2one("pos.payment.method")

    pos_session_id = fields.Many2one("pos.session")
    move_id = fields.Many2one("account.move", "Invoice", domain="[ ('type', '=', 'out_invoice') ]")

    @api.model
    def create(self, vals_list):

        if "name" not in vals_list:
            name = self.env["ir.sequence"].next_by_code('seq.pos.payment.register.invoice.payment')
            vals_list["name"] = name

        return super().create(vals_list)

    def pay_invoice(self):
        pos_session_ids = self.mapped("pos_session_id")
        for pos_session_id in pos_session_ids:
            journal_id = pos_session_id.config_id.journal_id
            invoice_payment_ids = pos_session_ids.invoice_payment_ids
            move_id, cash_line_ids = invoice_payment_ids._create_payment_miscellaneous_move(journal_id)
            invoice_payment_ids._create_statements_and_reconcile_with_cash_line_ids(cash_line_ids)
            invoice_payment_ids._reconcile_miscellaneous_move_with_invocies(move_id)
            pos_session_id.invoice_payment_move_id = move_id

    def _create_payment_miscellaneous_move(self, journal_id):
        payment_miscellaneous_move_id = self.env["account.move"].create({
            "journal_id": journal_id.id
        })

        journal_items = self._build_miscellaneous_moves_journal_items(payment_miscellaneous_move_id)
        receivable_per_invoice_and_partner = self._build_invoice_partner_receivable_journal_items(payment_miscellaneous_move_id)

        account_move_line_env = self.env["account.move.line"].with_context(check_move_validity=False)
        pos_line_ids = account_move_line_env.create(journal_items)
        pos_partner_invoice_receivable_line_ids = account_move_line_env.create(receivable_per_invoice_and_partner)

        payment_miscellaneous_move_id.post()

        pos_cash_line_ids = pos_line_ids.filtered("pos_payment_method_id.is_cash_count")

        return payment_miscellaneous_move_id, pos_cash_line_ids

    def _build_miscellaneous_moves_journal_items(self, move_id):
        payment_method_amounts = self._get_payment_method_amounts()
        journal_items = []

        for payment_method_id, amount in payment_method_amounts.items():
            payment_method_id = self.env["pos.payment.method"].browse([payment_method_id])
            receivable_account_id = payment_method_id.receivable_account_id

            journal_items.append({
                "account_id": receivable_account_id.id,
                "debit": amount,
                "name": payment_method_id.name,
                "move_id": move_id.id,
                "pos_payment_method_id": payment_method_id.id,
                "partner_id": False,
            })
        return journal_items

    def _build_invoice_partner_receivable_journal_items(self, move_id):
        # Do literally nothing
        a = 0
        payment_method_amounts = self._get_payment_method_amounts()
        journal_items = []

        for payment_method_id in payment_method_amounts.keys():
            payment_method_id = self.env["pos.payment.method"].browse([payment_method_id])

            invoice_payment_filtered_by_payment_method = self.filtered(lambda invoice_payment: invoice_payment.payment_method_id == payment_method_id)
            partner_ids = invoice_payment_filtered_by_payment_method.mapped("move_id.partner_id")

            for partner_id in partner_ids:

                move_ids = invoice_payment_filtered_by_payment_method.mapped("move_id")
                receivable_account_ids = invoice_payment_filtered_by_payment_method.mapped("move_id").get_receivable_account_ids()
                for receivable_account_id in receivable_account_ids:

                    move_ids_with_receivable = move_ids.filtered(lambda move: move.get_receivable_account_ids()[0] == receivable_account_id)

                    amount = sum(invoice_payment_filtered_by_payment_method
                                 .filtered(lambda invoice_payment:
                                           invoice_payment.move_id.partner_id == partner_id
                                           and invoice_payment.move_id.id in move_ids_with_receivable.ids)
                                 .mapped("payment_amount"))

                    journal_items.append({
                        "partner_id": partner_id.id,
                        "account_id": receivable_account_id.id,
                        "credit": amount,
                        "name": payment_method_id.name,
                        "move_id": move_id.id,
                        "pos_payment_method_id": payment_method_id.id
                    })
        return journal_items

    def _create_statements_and_reconcile_with_cash_line_ids(self, cash_line_ids):
        pos_session_id = self.pos_session_id.ensure_one()

        payment_method_amounts = self._get_payment_method_amounts(cash=True)
        statements_by_journal_id = {statement.journal_id.id: statement for statement in pos_session_id.statement_ids}

        lines_ids_to_reconcile = cash_line_ids

        for payment_method_id, amount in payment_method_amounts.items():
            payment_method_id = self.env["pos.payment.method"].browse([payment_method_id])

            statement = statements_by_journal_id[payment_method_id.cash_journal_id.id]

            statement_line_values = pos_session_id._get_statement_line_vals(statement, payment_method_id.receivable_account_id, amount)
            BankStatementLine = self.env['account.bank.statement.line']
            statement_line = BankStatementLine.create(statement_line_values)

            if not pos_session_id.config_id.cash_control:
                statement.write({'balance_end_real': statement.balance_end})

            statement.button_confirm_bank()
            if not statement_line.journal_entry_ids:
                statement_line.fast_counterpart_creation()
            lines_ids_to_reconcile += statement_line.journal_entry_ids.filtered(lambda aml: aml.account_id.internal_type == 'receivable')

        accounts = lines_ids_to_reconcile.mapped('account_id')
        lines_by_account = [lines_ids_to_reconcile.filtered(lambda l: l.account_id == account) for account in accounts]
        for lines in lines_by_account:
            lines.reconcile()

    def _get_payment_method_amounts(self, cash=False):
        payment_method_amounts = {}

        payment_method_ids = self.mapped("payment_method_id")

        if cash:
            payment_method_ids = payment_method_ids.filtered("is_cash_count")

        for payment_method_id in payment_method_ids:
            payment_amount = sum(self.filtered(lambda invoice_payment: invoice_payment.payment_method_id == payment_method_id).mapped("payment_amount"))
            payment_method_amounts[payment_method_id.id] = payment_amount

        return payment_method_amounts

    def _reconcile_miscellaneous_move_with_invocies(self, move_id):
        # pos_session_id = self.pos_session_id.ensure_one()
        invoice_ids = self.mapped("move_id")
        invoice_receivable_lines = invoice_ids.get_receivable_line_ids()
        payment_lines = move_id.line_ids.filtered(lambda line_id: line_id.account_id in invoice_receivable_lines.mapped("account_id") and line_id.partner_id)

        lines_by_account = invoice_receivable_lines + payment_lines

        accounts = lines_by_account.mapped('account_id')
        lines_by_account = [lines_by_account.filtered(lambda l: l.account_id == account) for account in accounts]
        for lines in lines_by_account:
            lines.reconcile()