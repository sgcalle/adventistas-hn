# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import fields, models, api, _


class PosSession(models.Model):
    _inherit = "pos.session"

    invoice_payment_ids = fields.One2many("pos_pr.invoice.payment", "pos_session_id")
    invoice_surcharge_ids = fields.One2many("pos_pr.invoice.surcharge", "pos_session_id")
    invoice_payment_amount = fields.Float(compute='_compute_cash_balance')
    invoice_payment_move_id = fields.Many2one("account.move", string="Invoice payment misc move")

    def _validate_session(self):
        action = super()._validate_session()

        if self.invoice_surcharge_ids:
            self.invoice_surcharge_ids.apply_surcharge()

            payment_ids = list(set(self.invoice_payment_ids.ids) | set(self.invoice_surcharge_ids.payment_ids.ids))

            self.invoice_payment_ids = payment_ids

        if self.invoice_payment_ids:
            self.invoice_payment_ids.pay_invoice()
        return action

    def _create_account_move(self):
        """ Create account.move and account.move.line records for this session.

        Side-effects include:
            - setting self.move_id to the created account.move record
            - creating and validating account.bank.statement for cash payments
            - reconciling cash receivable lines, invoice receivable lines and stock output lines
        """

        journal = self.config_id.journal_id
        # Passing default_journal_id for the calculation of default currency of account move
        # See _get_default_currency in the account/account_move.py.
        account_move = self.env['account.move'].with_context(default_journal_id=journal.id).create({
            'journal_id': journal.id,
            'date': fields.Date.context_today(self),
            'ref': self.name,
        })
        self.write({'move_id': account_move.id})

        data = {}
        data = self._accumulate_amounts(data)
        data = self._create_non_reconciliable_move_lines(data)
        data = self._create_cash_statement_lines_and_cash_move_lines(data)

        # We need to clear partner due it causes that the partner ledger goes wrong
        self.move_id.line_ids.with_context(check_move_validity=False).partner_id = False

        # Now here is where we add the partner to the receivable lines
        # Thanks odoo!

        data = self._create_invoice_receivable_lines(data)
        data = self._create_stock_output_lines(data)
        data = self._create_extra_move_lines(data)
        data = self._reconcile_account_move_lines(data)

    def _create_invoice_receivable_lines(self, data):

        MoveLine = data.get('MoveLine')
        payment_move_line_values = self._build_payment_receivable_lines()
        invoice_receivable_lines = {}

        payment_move_line_ids = MoveLine.create(payment_move_line_values)
        for account_id in payment_move_line_ids.mapped("account_id"):
            invoice_receivable_lines[account_id.id] \
                = payment_move_line_ids.filtered(lambda line: line.account_id == account_id)

        data.update({"invoice_receivable_lines": invoice_receivable_lines})

        return data

    def _build_payment_receivable_lines(self):
        self.ensure_one()
        grouped_invoice_payments = self._group_invoice_payments()
        payment_receivable_lines = self._build_payments_move_line_values(grouped_invoice_payments)
        return payment_receivable_lines

    def _group_invoice_payments(self):
        grouped_invoice_payments = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: {'amount': 0.0, 'amount_converted': 0.0})))

        for order_id in self.order_ids.filtered(lambda order: order.is_invoiced):
            for payment_id in order_id.payment_ids:
                amount = payment_id.amount
                date = payment_id.payment_date
                receivalbe_account_id = order_id.get_receivable_account()
                payment_method_id = payment_id.payment_method_id

                partner_id = self.env["res.partner"]._find_accounting_partner(order_id.partner_id)

                new_amount = self._update_amounts(
                    grouped_invoice_payments[partner_id][receivalbe_account_id][payment_method_id],
                    {'amount': amount}, date)

                grouped_invoice_payments[partner_id][receivalbe_account_id][payment_method_id] = new_amount

        return grouped_invoice_payments

    def _build_payments_move_line_values(self, grouped_invoice_payments):
        # invoice_receivable_vals = defaultdict(lambda: defaultdict(list))
        payment_move_lines = []
        for partner_id, partner_amounts in grouped_invoice_payments.items():
            for receivable_account_id, receivable_amounts in partner_amounts.items():
                for payment_method_id, amounts in receivable_amounts.items():
                    receivable_line_vals = self._get_invoice_receivable_vals(receivable_account_id.id,
                                                                             amounts['amount'],
                                                                             amounts['amount_converted'])

                    # If partner doesn't have company, partner_id in the receivable account will be different

                    resposible_partner_id = self.env["res.partner"]._find_accounting_partner(partner_id)

                    receivable_line_vals["pos_payment_method_id"] = payment_method_id.id
                    receivable_line_vals["partner_id"] = resposible_partner_id.id

                    # invoice_receivable_vals[partner_id][receivable_account_id].append(receivable_line_vals)
                    payment_move_lines.append(receivable_line_vals)
        return payment_move_lines

    @api.depends('payment_method_ids', 'order_ids', 'cash_register_balance_start', 'cash_register_id',
                 'invoice_payment_ids')
    def _compute_cash_balance(self):
        for session in self:
            cash_payment_method_ids = session.payment_method_ids.filtered('is_cash_count')

            if cash_payment_method_ids:
                transaction_total_amount = session.get_cash_transaction_total_amount()
                total_cash_invoice_payment_amount = 0.0 if session.state == 'closed' else sum(
                    session.invoice_payment_ids.filtered("payment_method_id.is_cash_count").mapped("display_amount"))

                cash_register_total_entry_encoding = self.cash_register_id.total_entry_encoding + transaction_total_amount + total_cash_invoice_payment_amount

                session.cash_register_total_entry_encoding = cash_register_total_entry_encoding
                session.invoice_payment_amount = sum(session.invoice_payment_ids.mapped("display_amount"))
                session.cash_register_balance_end = session.cash_register_balance_start + session.cash_register_total_entry_encoding
                session.cash_register_difference = session.cash_register_balance_end_real - session.cash_register_balance_end
            else:
                session.cash_register_total_entry_encoding = 0.0
                session.cash_register_balance_end = 0.0
                session.cash_register_difference = 0.0

    def get_cash_transaction_total_amount(self):
        self.ensure_one()
        cash_payment_method_ids = self.payment_method_ids.filtered('is_cash_count')
        cash_register_total_entry_encoding = 0.0

        for cash_payment_method in cash_payment_method_ids:
            total_cash_payment = sum(self.order_ids.mapped('payment_ids').filtered(
                lambda payment: payment.payment_method_id == cash_payment_method).mapped('amount'))
            # cash_register_total_entry_encoding += (0.0 if self.state == 'closed' else total_cash_payment)
            cash_register_total_entry_encoding += total_cash_payment  # (0.0 if self.state == 'closed' else total_cash_payment)

        # cash_register_total_entry_encoding += self.cash_register_id.total_entry_encoding
        return cash_register_total_entry_encoding
