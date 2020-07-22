# -*- encoding: utf-8 -*-

from ..utils import formatting

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

SELECT_PERSON_TYPES = [
    ("student", "Student"),
    ("parent", "Parent")
]

SELECT_COMPANY_TYPES = [
    ("person", "Person"),
    ("company", "Company/Family")
]

SELECT_STATUS_TYPES = [
    ("admissions", "Admissions"),
    ("enrolled", "Enrolled"),
    ("graduate", "Graduate"),
    ("inactive", "Inactive"),
    ("pre-enrolled", "Pre-Enrolled"),
    ("withdrawn", "Withdrawn"),
]


class Contact(models.Model):
    """ We inherit to enable School features for contacts """

    _inherit = "res.partner"

    # Overwritten fields
    # Name should be readonly
    name = fields.Char(index=True, compute="_compute_name", store=True, readonly=True)

    company_type = fields.Selection(SELECT_COMPANY_TYPES, string="Company Type")
    person_type = fields.Selection(SELECT_PERSON_TYPES, string="Person Type")

    grade_level_id = fields.Many2one("school_base.grade_level", string="Grade Level")
    homeroom = fields.Char("Homeroom")

    student_status = fields.Char("Student status", help="(This field is deprecated)")

    comment_facts = fields.Text("Facts Comment")
    family_ids = fields.Many2many("res.partner", string="Families", relation="partner_families", column1="partner_id",
                                  column2="partner_family_id")
    member_ids = fields.Many2many("res.partner", string="Members", relation="partner_members", column1="partner_id",
                                  column2="partner_member_id")

    facts_id_int = fields.Integer("Fact id (Integer)")
    facts_id = fields.Char("Fact id")
    facts_approved = fields.Boolean()

    is_family = fields.Boolean("Is a family?")

    # For Families
    financial_res_ids = fields.Many2many("res.partner", string="Financial responsability",
                                         relation="partner_financial_res", column1="partner_id",
                                         column2="partner_financial_id")

    first_name = fields.Char("First Name")
    middle_name = fields.Char("Middle Name")
    last_name = fields.Char("Last Name")

    date_of_birth = fields.Date()
    student_status_id = fields.Selection(SELECT_STATUS_TYPES, string="Student status")
    student_next_status_id = fields.Selection(SELECT_STATUS_TYPES, string="Student next status")
    allergy_ids = fields.One2many("school_base.allergy", "partner_id", string="Allergies")
    condition_ids = fields.One2many("school_base.condition", "partner_id", string="Conditions")

    @api.depends("first_name", "middle_name", "last_name")
    def _compute_name(self):
        for record in self:
            record.name = formatting.format_name(record.first_name, record.middle_name, record.last_name)

    @api.model
    def create(self, values):
        PartnerEnv = self.env["res.partner"]

        # Some constant for making more readeable the code
        ACTION_TYPE = 0
        TYPE_REPLACE = 6
        TYPE_ADD_EXISTING = 4
        TYPE_REMOVE_NO_DELETE = 3

        if "name" not in values:
            first_name = values["first_name"] if "first_name" in values else ""
            middle_name = values["first_name"] if "middle_name" in values else ""
            last_name = values["last_name"] if "last_name" in values else ""

            values["name"] = formatting.format_name(first_name, middle_name, last_name)
        partners = super().create(values)

        ctx = self._context
        for record in partners:
            if "member_id" in ctx:
                if ctx.get("member_id"):
                    record.write({
                        "member_ids": [[TYPE_ADD_EXISTING, ctx.get("member_id"), False]]
                    })
                else:
                    raise UserError(_("Contact should be save before adding families"))

        return partners

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
