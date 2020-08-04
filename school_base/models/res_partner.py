# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

from ..utils.commons import switch_statement

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
    allow_edit_student_name = fields.Boolean(compute="_retrieve_allow_name_edit_from_config")
    allow_edit_parent_name = fields.Boolean(compute="_retrieve_allow_name_edit_from_config")
    allow_edit_person_name = fields.Boolean(compute="_retrieve_allow_name_edit_from_config")

    is_name_edit_allowed = fields.Boolean(compute="_compute_allow_name_edition")

    def _retrieve_allow_name_edit_from_config(self):
        self.allow_edit_student_name = self.env["ir.config_parameter"].get_param(
            "school_base.allow_edit_student_name") != False
        self.allow_edit_parent_name = self.env["ir.config_parameter"].get_param(
            "school_base.allow_edit_parent_name") != False
        self.allow_edit_person_name = self.env["ir.config_parameter"].get_param(
            "school_base.allow_edit_person_name") != False

    @api.depends("allow_edit_student_name",
                 "allow_edit_parent_name",
                 "allow_edit_person_name",
                 "person_type")
    def _compute_allow_name_edition(self):
        for partner_id in self:
            # Sumulating switch statement
            partner_id.is_name_edit_allowed = switch_statement(cases={
                "default": partner_id.allow_edit_person_name,
                "parent": partner_id.allow_edit_parent_name,
                "student": partner_id.allow_edit_student_name,
            }, value=partner_id.person_type)

    @api.onchange("person_type")
    def _onchange_person_type(self):
        self._compute_allow_name_edition()

    name = fields.Char(index=True, compute="_compute_name", store=True)

    company_type = fields.Selection(SELECT_COMPANY_TYPES, string="Company Type")
    person_type = fields.Selection(SELECT_PERSON_TYPES, string="Person Type")

    grade_level_id = fields.Many2one("school_base.grade_level", string="Grade Level")
    homeroom = fields.Char("Homeroom")

    student_status = fields.Char("Student status (Deprecated)", help="(This field is deprecated)")

    comment_facts = fields.Text("Facts Comment")
    family_ids = fields.Many2many("res.partner", string="Families", relation="partner_families", column1="partner_id",
                                  column2="partner_family_id")
    member_ids = fields.Many2many("res.partner", string="Members", relation="partner_members", column1="partner_id",
                                  column2="partner_member_id")

    facts_id_int = fields.Integer("Facts id (Integer)")
    facts_id = fields.Char("Facts id")
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

    # old_name = fields.Char()
    _sql_constraints = [
        ('facts_id_unique', 'unique(facts_id)', 'Another contact has the same facts id!'),
        ('facts_id_int_unique', 'unique(facts_id_int)', 'Another contact has the same facts id!'),
    ]

    @api.model
    def format_name(self, first_name, middle_name, last_name):
        """
        This will format everything depending of school base settings
        :return: A String with the formatted version
        """

        name_order_relation = {self.env.ref("school_base.name_sorting_first_name"): first_name or "",
                               self.env.ref("school_base.name_sorting_middle_name"): middle_name or "",
                               self.env.ref("school_base.name_sorting_last_name"): last_name or ""}

        name_sorting_ids = self.env.ref("school_base.name_sorting_first_name") + \
                           self.env.ref("school_base.name_sorting_middle_name") + \
                           self.env.ref("school_base.name_sorting_last_name")

        name = ""
        sorted_name_sorting_ids = name_sorting_ids.sorted("sequence")
        for sorted_name_id in sorted_name_sorting_ids:
            name += (sorted_name_id.prefix or "") + \
                    name_order_relation.get(sorted_name_id, "") + \
                    (sorted_name_id.sufix or "")

        return name

    def auto_format_name(self):
        """ Use format_name method to create that """
        # partner_ids = self.filtered(lambda partner: partner_id)
        for partner_id in self:
            first = partner_id.first_name
            middle = partner_id.middle_name
            last = partner_id.last_name

            if not partner_id.is_company and not partner_id.is_family and any([first, middle, last]):
                # old_name = partner_id.name
                partner_id.name = partner_id.format_name(first, middle, last)
            else:
                partner_id.name = partner_id.name

    @api.onchange("first_name", "middle_name", "last_name")
    def _onchange_name_fields(self):
        self.auto_format_name()

    @api.depends("first_name", "middle_name", "last_name")
    def _compute_name(self):
        self.auto_format_name()

    @api.model
    def create(self, values):
        """ Student custom creation for family relations and other stuffs """

        # Some constant for making more readeable the code
        # ACTION_TYPE = 0
        # TYPE_REPLACE = 6
        TYPE_ADD_EXISTING = 4
        # TYPE_REMOVE_NO_DELETE = 3

        if "name" not in values:
            first_name = values["first_name"] if "first_name" in values else ""
            middle_name = values["first_name"] if "middle_name" in values else ""
            last_name = values["last_name"] if "last_name" in values else ""

            values["name"] = self.format_name(first_name, middle_name, last_name)
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
        """ Student custom creation for family relations and other stuffs """

        # Some constant for making more readeable the code
        ACTION_TYPE = 0
        TYPE_REPLACE = 6
        TYPE_ADD_EXISTING = 4
        TYPE_REMOVE_NO_DELETE = 3

        for record in self:
            if "family_ids" in values:
                for m2m_action in values["family_ids"]:
                    if m2m_action[ACTION_TYPE] == TYPE_REPLACE:
                        partner_ids = self.browse(m2m_action[2])
                        removed_parter_ids = self.browse(set(record.family_ids.ids) - set(m2m_action[2]))
                        partner_ids.write({
                            "member_ids": [[TYPE_ADD_EXISTING, record.id, False]],
                        })
                        removed_parter_ids.write({
                            "member_ids": [[TYPE_REMOVE_NO_DELETE, record.id, False]],
                        })

            if "member_ids" in values:
                for m2m_action in values["member_ids"]:
                    if m2m_action[ACTION_TYPE] == TYPE_REPLACE:
                        partner_ids = self.browse(m2m_action[2])
                        removed_parter_ids = self.browse(set(record.family_ids.ids) - set(m2m_action[2]))
                        partner_ids.write({
                            "family_ids": [[TYPE_ADD_EXISTING, record.id, False]],
                        })
                        removed_parter_ids.write({
                            "family_ids": [[TYPE_REMOVE_NO_DELETE, record.id, False]],
                        })

        return super().write(values)
