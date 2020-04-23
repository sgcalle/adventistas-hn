# -*- coding: utf-8 -*-

from odoo import models, fields


class SchoolCode(models.Model):
    _name = "school_base.school_code"
    _order = "sequence"
    _description = "School code"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)


class SchoolYear(models.Model):
    _name = "school_base.school_year"
    _order = "sequence"
    _description = "School year"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
    school_code_id = fields.Many2one("school_base.school_code", string="School code")


class GradeLevel(models.Model):
    _name = "school_base.grade_level"
    _order = "sequence"
    _description = "The grade level"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
    school_code_id = fields.Many2one("school_base.school_code", string="School code")
