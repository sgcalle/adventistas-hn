#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    payroll_bill_product_id = fields.Many2one(string="Payroll Bill Product",
        comodel_name="product.product")
    payroll_invoice_product_id = fields.Many2one(string="Payroll Invoice Product",
        comodel_name="product.product")
    payroll_journal_id = fields.Many2one(string="Payroll Journal",
        comodel_name="account.journal")