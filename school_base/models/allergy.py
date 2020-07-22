# -*- coding: utf-8 -*-

from odoo import models, fields


class Allergy(models.Model):
    _name = "school_base.allergy"
    _description = "Allergies for contacts (students or somebody else)"

    name = fields.Char("Description")
    partner_id = fields.Many2one("res.partner", "Contact")
