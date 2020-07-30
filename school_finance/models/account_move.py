# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMove(models.Model):
    """ Added school finance functionalities """
    _inherit = "account.move"

    student_id = fields.Many2one("res.partner", string="Student", domain=[('person_type', '=', 'student')])
    family_id = fields.Many2one("res.partner", string="Family", domain=[('is_family', '=', True)])

    family_members_ids = fields.Many2many(related="family_id.member_ids")

    receivable_account_id = fields.Many2one("account.account", string="Receivable account", domain=[("user_type_id.type", "=", "receivable")])

    def _compute_grade_level(self):
        for move_id in self:
            move_id.student_grade_level = move_id.student_id.grade_level_id

    student_grade_level = fields.Many2one("school_base.grade_level",
                                          compute="_compute_grade_level",
                                          string="Grade level", store=True)

    def _compute_student_homeroom(self):
        for move_id in self:
            move_id.student_homeroom = move_id.student_id.homeroom

    student_homeroom = fields.Char(compute="_compute_student_homeroom", string="Student homeroom", store=True)

    def set_receivable_account(self):
        """ It uses receivable_account_id field to set autoamtically the receivable account """
        for record in self:
            receivable_line_id = record.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type == 'receivable')
            receivable_line_id.ensure_one()
            if receivable_line_id and record.receivable_account_id:
                receivable_line_id.account_id = record.receivable_account_id.id

