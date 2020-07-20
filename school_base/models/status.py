# -*- encoding: utf-8 -*-

from ..utils import formatting

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class SchoolBaseStatus(models.Model):
    """ School status for students """

    _name = "school_base.status"
    _description = "School status for students"
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
