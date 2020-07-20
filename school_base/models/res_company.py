# -*- encoding: utf-8 -*-

from ..utils import formatting

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    district_code_id = fields.Many2one("school_base.district_code", "District code")
    district_code_name = fields.Char(related="district_code_id.name")
