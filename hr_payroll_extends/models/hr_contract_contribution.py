#-*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrContractContribution(models.Model):
    _name = "hr.contract.contribution"
    _description = "Contract Pay Contribution"

    name = fields.Char(string="Reference",
        required=True)
    partner_id = fields.Many2one(string="Partner",
        comodel_name="res.partner",
        required=True)
    contract_id = fields.Many2one(string="Contract",
        comodel_name="hr.contract",
        required=True,
        ondelete="cascade")
    amount = fields.Float(string="Amount",
        required=True,
        help="If % of Wage is checked, this is the ratio of the contribution based on the wage in the contract. Otherwise, this is a fixed amount.")
    percentage_of_wage = fields.Boolean(string="% of Wage",
        help="Check if the contribution amount is a percentage of the wage in the contract.")
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
    
    @api.depends("amount", "employee_percent", "company_percent", "percentage_of_wage", "contract_id.wage")
    def _compute_amount(self):
        for contrib in self:
            amount = (contrib.contract_id.wage * contrib.amount / 100.0) if contrib.percentage_of_wage else contrib.amount
            contrib.employee_amount = amount * contrib.employee_percent / 100.0
            contrib.company_amount = amount * contrib.company_percent / 100.0