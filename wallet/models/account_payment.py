# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.depends("reconciled_invoice_ids")
    def _compute_paid_amount(self):
        for payment_id in self:
            invoices = payment_id.reconciled_invoice_ids
            if invoices:
                invoices_sum = sum(invoices.mapped(lambda inv: payment_id._get_invoice_payment_amount(inv._origin)))
                payment_id.paid_amount = invoices_sum
            else:
                payment_id.paid_amount = 0.0

    @api.depends("reconciled_invoice_ids")
    def _compute_unpaid_amount(self):
        for payment_id in self:
            payment_id.unpaid_amount = payment_id.amount - payment_id.paid_amount

    paid_amount = fields.Monetary(compute="_compute_paid_amount", store=True)
    unpaid_amount = fields.Monetary(compute="_compute_unpaid_amount", store=True)
    wallet_id = fields.Many2one("wallet.category")
