#-*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrContractContribution(models.Model):
    _name = "hr.contract.contribution"
    _description = "Contract Pay Contribution"

    name = fields.Char(string="Reference",
        required=True)
    contract_id = fields.Many2one(string="Contract",
        comodel_name="hr.contract",
        required=True)
    amount = fields.Float(string="Amount",
        required=True)
    employee_percent = fields.Float(string="Emp. %")
    company_percent = fields.Float(string="Comp. %")
    employee_amount = fields.Float(string="Emp. Amount",
        compute="_compute_amount")
    company_amount = fields.Float(string="Comp. Amount",
        compute="_compute_amount")

    @api.constrains("employee_percent", "company_percent")
    def _check_percents(self):
        for contrib in self:
            if contrib.employee_percent < 0.0 or contrib.company_percent < 0.0:
                raise ValidationError("Contribution percentage must be greater than 0.")
            if (contrib.employee_percent + contrib.company_percent) != 100.0:
                raise ValidationError("Employee and Company percentage must total to 100.")
    
    @api.depends("amount", "employee_percent", "company_percent")
    def _compute_amount(self):
        for contrib in self:
            contrib.employee_amount = contrib.amount * contrib.employee_percent / 100.0
            contrib.company_amount = contrib.amount * contrib.company_percent / 100.0