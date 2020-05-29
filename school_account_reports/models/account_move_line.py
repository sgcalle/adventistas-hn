# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    student_id = fields.Many2one(string='Student',
        comodel_name='res.partner',
        compute='_compute_student_id',
        store=True)
    
    @api.depends('name', 'move_id', 'move_id.student_id',
                 'matched_debit_ids','matched_debit_ids.debit_move_id.move_id.student_id',
                 'matched_credit_ids','matched_credit_ids.credit_move_id.move_id.student_id')
    def _compute_student_id(self):
        for line in self:
            result = False
            if line.move_id.student_id:
                result = line.move_id.student_id.id
            if not result and line.matched_debit_ids:
                for debit in line.matched_debit_ids:
                    if debit.debit_move_id.move_id.student_id:
                        result = debit.debit_move_id.move_id.student_id.id
                        break
            if not result and line.matched_credit_ids:
                for credit in line.matched_credit_ids:
                    if credit.credit_move_id.move_id.student_id:
                        result = credit.credit_move_id.move_id.student_id.id
                        break
            line.student_id = result