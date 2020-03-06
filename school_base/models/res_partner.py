# -*- encoding: utf-8 -*-

from odoo import fields, models

selec_person_types = [
    ("student", "Student"),
    ("parent", "Parent")
]

selec_company_types = [
    ("person", "Person"),
    ("company", "Family")
]

class Contact(models.Model):
    _inherit = "res.partner"

    company_type = fields.Selection(selec_company_types, string="Company Type")
    person_type = fields.Selection(selec_person_types, string="Person Type")

    grade_level_id = fields.Many2one("school_base.grade_level", string="Grade Level")
    homeroom = fields.Char("Homeroom")    
    student_status = fields.Char("Student status")

    comment_facts = fields.Text("Facts Comment")
    family_ids = fields.Many2many("res.partner", string="Families", relation="partner_families", column1="partner_id", column2="partner_family_id")
    member_ids = fields.Many2many("res.partner", string="Members", relation="partner_members", column1="partner_id", column2="partner_member_id")

    family_invoice_ids = fields.Many2many("account.move")
    facts_id_int = fields.Integer("Fact id (Integer)")
    facts_id = fields.Char("Fact id")

    # def write(self, values):
    #     PartnerEnv = self.env["res.partner"]


    #     return super().write(values)