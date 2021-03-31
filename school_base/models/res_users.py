# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    district_code_id = fields.Many2one('school_base.district_code', string="District code")
    school_code_id = fields.Many2one('school_base.school_code', string="School code")

    district_code_ids = fields.Many2many('school_base.district_code', string="District codes")
    school_code_ids = fields.Many2many('school_base.school_code', string="School codes")
