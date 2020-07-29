# -*- coding: utf-8 -*-

from odoo import models, fields


class Condition(models.Model):
    _name = "school_base.condition"
    _description = "Conditions for contacts (students or somebody else)"

    name = fields.Char("Description")
    partner_id = fields.Many2one("res.partner", "Contact")
