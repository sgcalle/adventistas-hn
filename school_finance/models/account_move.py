# -*- coding: utf-8 -*-

from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = "account.move"

    student_id = fields.Many2one("res.partner", string="Student", domain=[('person_type', '=', 'student')])
    family_id = fields.Many2one("res.partner", string="Family", domain=[('is_family', '=', True)])

    family_members_ids = fields.Many2many(related="family_id.member_ids")


    @api.onchange("student_id")
    def _onchange_student_id(self):
        return self._onchange_partner_id()
    
    def _recompute_payment_terms_lines(self):
        res = super(AccountMove, self)._recompute_payment_terms_lines()
        if self.student_id:
            for line in self.line_ids.filtered(lambda l: l.account_id.internal_type == "receivable"):
                line.account_id = self.student_id.property_account_receivable_id.id
        return res

class AccountJournal(models.Model):
    _inherit = "account.journal"

    facts_accounting_system_id = fields.Integer("Accounting System")
    template_with_payment_id = fields.Many2one("ir.ui.view", string="Template with payment",
                                                 domain=[("type", "=", "qweb")], default=lambda self: self.env.ref('account.report_invoice_document_with_payments'))
    template_id = fields.Many2one("ir.ui.view", string="Template without payment",
                                   domain=[("type", "=", "qweb")], default=lambda self: self.env.ref('account.report_invoice_document'))