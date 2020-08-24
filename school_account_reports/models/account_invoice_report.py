# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    student_id = fields.Many2one("res.partner", "Student", readonly=True)

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", move.student_id as student_id"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", move.student_id"