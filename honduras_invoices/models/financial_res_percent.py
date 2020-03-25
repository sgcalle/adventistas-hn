# -*- coding: utf-8 -*-

from odoo import models, fields

class FinacialResponsabilityPercent(models.Model):
    _name = "honduras_invoices.financial.res.percent"
    _description = "Realted model to finance responsabilty"

    family_id = fields.Many2one("res.partner", required=True, string="Family", domain=['&', ("is_family", "=", True), ('is_company', '=', True)])
    category_id = fields.Many2one("product.category", required=True, string="Category", domain=[("parent_id", "=", False)])
    percent = fields.Integer("Percent")

    partner_id = fields.Many2one("res.partner", string="Customer", domain=[("is_family", "=", False)])
