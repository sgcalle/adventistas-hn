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

    family_invoice_ids = fields.Many2many("account.move", compute="_compute_family_invoice_ids", domain=[('type', '=', 'out_invoice')], context={'default_type': 'out_invoice', 'type': 'out_invoice','tree_view_ref': 'account.view_invoice_tree'})
    facts_id_int = fields.Integer("Fact id (Integer)")
    facts_id = fields.Char("Fact id")

    is_family = fields.Boolean("Is a family?")
    invoice_address_id = fields.Many2one("res.partner", string="Invoice Address")
    
    # For Families
    financial_res_ids = fields.Many2many("res.partner", string="Financial responsability", relation="partner_financial_res", column1="partner_id", column2="partner_financial_id")

    def _compute_family_invoice_ids(self):
        for record in self:
            invoices = False
            if record.is_company:
                invoices = self.member_ids.invoice_ids + self.invoice_ids
            record.family_invoice_ids = invoices

                
    def write(self, values):
        PartnerEnv = self.env["res.partner"]

        # Some constant for making more readeable the code
        ACTION_TYPE = 0
        TYPE_REPLACE = 6
        TYPE_ADD_EXISTING = 4
        TYPE_REMOVE_NO_DELETE = 3

        for record in self:
            if "family_ids" in values:
                for m2m_action in values["family_ids"]:
                    if m2m_action[ACTION_TYPE] == TYPE_REPLACE:
                        partner_ids = PartnerEnv.browse(m2m_action[2])
                        removed_parter_ids = PartnerEnv.browse(set(record.family_ids.ids) - set(m2m_action[2]))
                        partner_ids.write({
                            "member_ids": [[TYPE_ADD_EXISTING, record.id, False]],
                        })
                        removed_parter_ids.write({
                            "member_ids": [[TYPE_REMOVE_NO_DELETE, record.id, False]],
                        })
                    
            if "member_ids" in values:
                for m2m_action in values["member_ids"]:
                    if m2m_action[ACTION_TYPE] == TYPE_REPLACE:
                        partner_ids = PartnerEnv.browse(m2m_action[2])
                        removed_parter_ids = PartnerEnv.browse(set(record.family_ids.ids) - set(m2m_action[2]))
                        partner_ids.write({
                            "family_ids": [[TYPE_ADD_EXISTING, record.id, False]],
                        })
                        removed_parter_ids.write({
                            "family_ids": [[TYPE_REMOVE_NO_DELETE, record.id, False]],
                        })

        return super().write(values)