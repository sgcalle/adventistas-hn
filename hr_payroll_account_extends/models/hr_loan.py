#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrLoan(models.Model):
    _inherit = "hr.loan"

    debit_account_id = fields.Many2one(string="Debit Account",
        comodel_name="account.account")
    credit_account_id = fields.Many2one(string="Credit Account",
        comodel_name="account.account")
    analytic_account_id = fields.Many2one(string="Analytic Account",
        comodel_name="account.analytic.account")