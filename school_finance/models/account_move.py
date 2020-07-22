# -*- coding: utf-8 -*-

from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    student_id = fields.Many2one("res.partner", string="Student", domain=[('person_type', '=', 'student')])
    family_id = fields.Many2one("res.partner", string="Family", domain=[('is_family', '=', True)])

    family_members_ids = fields.Many2many(related="family_id.member_ids")

    receivable_account_id = fields.Many2one("account.account", string="Receivable account", domain=[("user_type_id.type", "=", "receivable")])

    def set_receivable_account(self):
        for record in self:
            receivable_line_id = record.line_ids.filtered(lambda record: record.account_id.user_type_id.type == 'receivable')
            receivable_line_id.ensure_one()
            if (receivable_line_id and record.receivable_account_id):
                receivable_line_id.account_id = record.receivable_account_id.id

