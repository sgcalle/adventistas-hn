# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    loan_ids = fields.One2many(string="Loans",
        comodel_name="hr.loan",
        inverse_name="employee_id",
        groups="hr_payroll.group_hr_payroll_user")
    loan_count = fields.Integer(string="Loan Count",
        compute="_compute_loan_count",
        groups="hr_payroll.group_hr_payroll_user")
    savings_ids = fields.One2many(string="Savings",
        comodel_name="hr.savings",
        inverse_name="employee_id",
        groups="hr_payroll.group_hr_payroll_user")
    savings_count = fields.Integer(string="Savings Count",
        compute="_compute_savings_count",
        groups="hr_payroll.group_hr_payroll_user")

    def _compute_loan_count(self):
        for employee in self:
            employee.loan_count = len(employee.loan_ids)
    
    def _compute_savings_count(self):
        for employee in self:
            employee.savings_count = len(employee.savings_ids)