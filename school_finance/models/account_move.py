# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove(models.Model):
    """ Added school finance functionalities """
    _inherit = "account.move"

    student_id = fields.Many2one("res.partner", string="Student", domain=[('person_type', '=', 'student')])
    family_id = fields.Many2one("res.partner", string="Family", domain=[('is_family', '=', True)])

    family_members_ids = fields.Many2many(related="family_id.member_ids")

    receivable_account_id = fields.Many2one("account.account", string="Receivable account", domain=[("user_type_id.type", "=", "receivable")])

    def get_receivable_account_ids(self):
        return self.get_receivable_line_ids().mapped("account_id")

    def get_receivable_line_ids(self):
        return self.mapped("line_ids").filtered(lambda line_id: line_id.account_id.user_type_id.type == 'receivable')

    @api.model
    def create(self, vals_list):
        move_id = super().create(vals_list)

        if move_id.student_id:
            move_id.student_grade_level = move_id.student_id.grade_level_id
            move_id.student_homeroom = move_id.student_id.homeroom

        return move_id

    student_grade_level = fields.Many2one("school_base.grade_level", readonly=True, string="Grade level")
    student_homeroom = fields.Char(readonly=True, string="Student homeroom")

    def set_receivable_account(self):
        """ It uses receivable_account_id field to set autoamtically the receivable account """
        for record in self:
            receivable_line_id = record.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type == 'receivable')
            receivable_line_id.ensure_one()
            if receivable_line_id and record.receivable_account_id:
                receivable_line_id.account_id = record.receivable_account_id.id

