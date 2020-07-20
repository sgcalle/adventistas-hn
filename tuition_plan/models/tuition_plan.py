# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TuitionPlan(models.Model):
    _name = "tuition.plan"
    _description = "Tuition Plan"

    name = fields.Char(string="Name",
        required=True)
    active = fields.Boolean(string="Active",
        default=True)
    accounting_date = fields.Date(string="Accounting Date",
        required=True,
        help="Used to identify what fiscal year this tuition plan belongs to")
    fiscal_year_date_from = fields.Date(string="Fiscal Year Start",
        compute="_compute_fiscal_year_dates",
        store=True,
        help="Autocomputed based on the selected accounting date")
    fiscal_year_date_to = fields.Date(string="Fiscal Year End",
        compute="_compute_fiscal_year_dates",
        store=True,
        help="Autocomputed based on the selected accounting date")
    category_id = fields.Many2one(string="Category",
        comodel_name="product.category",
        required=True,
        domain="[('parent_id','=',False)]",
        help="Category of the products included in this tuition plan")
    automation = fields.Selection(string="Automation",
        selection=[
            ("quotation", "Create Quotation"),
            ("sales_order", "Create Sales Order"),
            ("draft_invoice", "Create Sales Order and Draft Invoice"),
            ("posted_invoice", "Create Sales Order and Posted Invoice")],
        required=True,
        default="quotation",
        help="Specify what will automatically be created when an installment of this tuition plan is executed")
    first_charge_date = fields.Date(string="First Charge Date",
        required=True,
        help="The first date of the installments")
    payment_term_id = fields.Many2one(string="Payment Terms",
        comodel_name="account.payment.term",
        help="Payment term for the order and/or invoice generated.")
    first_due_date = fields.Date(string="First Due Date",
        help="Select the day of the due date. Only the day is used. Required if no payment term is set.")
    discount_ids = fields.One2many(string="Multi-child Discounts",
        comodel_name="tuition.plan.discount",
        inverse_name="plan_id",
        help="Discounts to apply based on the number of enrolled students in a family. Only enrolled students with the birthday set is included.")
    installment_ids = fields.One2many(string="Installments",
        comodel_name="tuition.plan.installment",
        inverse_name="plan_id",
        help="Installment dates generated for the tuition plan based on the first charge date")
    product_ids = fields.One2many(string="Products",
        comodel_name="tuition.plan.product",
        inverse_name="plan_id",
        help="Product to include in the order and/or invoice generated")
    company_id = fields.Many2one(string="Company",
        comodel_name="res.company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company)
    grade_level_ids = fields.Many2many(string="Grade Levels",
        comodel_name="school_base.grade_level",
        required=True,
        help="Grade levels to which this tuition plan applies and to whom it will generate order/invoice for")
    analytic_account_id = fields.Many2one(string="Analytic Account",
        comodel_name="account.analytic.account")
    default = fields.Boolean(string="Default",
        help="Specify if this tuition plan should be auto-assigned to students if they don't have any that overlaps with this plan")
    partner_ids = fields.Many2many(string="Students",
        comodel_name="res.partner",
        relation="partner_tuition_plan_rel",
        domain="[('grade_level_id','in',grade_level_ids)]",
        help="Students to which this tuition plan was manually assigned")
    discount_product_id = fields.Many2one(string="Discount Product",
        comodel_name="product.product",
        help="Product to use when adding multi-child discount lines")
    default_partner_ids = fields.Many2many(string="Default Students",
        comodel_name="res.partner",
        compute="_compute_default_partner_ids")

    @api.constrains("default", "grade_level_ids", "fiscal_year_date_from", "fiscal_year_date_to", "category_id", "active")
    def _check_default(self):
        for plan in self.filtered(lambda p: p.default):
            matched = self.search([
                "&", ("id","!=",plan.id),
                "&", ("default","=",True),
                "&", ("category_id","=",plan.category_id.id),
                "&", ("grade_level_ids","in",plan.grade_level_ids.ids),
                "|", ("fiscal_year_date_from","=",plan.fiscal_year_date_from),
                     ("fiscal_year_date_to","=",plan.fiscal_year_date_to)], limit=1)
            if matched:
                raise ValidationError(
                    "Unable to set as default. This tuition plan overlaps with %s (ID %d)." % (matched.name, matched.id))
    
    @api.constrains("partner_ids", "grade_level_ids", "fiscal_year_date_from", "fiscal_year_date_to", "category_id", "active")
    def _check_partner_ids(self):
        for plan in self:
            plan.partner_ids._check_tuition_plan_ids()

    @api.depends("accounting_date")
    def _compute_fiscal_year_dates(self):
        for plan in self:
            date_from = False
            date_to = False
            if plan.accounting_date:
                dates = plan.company_id.compute_fiscalyear_dates(plan.accounting_date)
                date_from = dates["date_from"]
                date_to = dates["date_to"]
            plan.fiscal_year_date_from = date_from
            plan.fiscal_year_date_to = date_to

    @api.constrains("first_charge_date")
    def _compute_installment_ids(self):
        for plan in self:
            plan.installment_ids.unlink()
            if not plan.first_charge_date:
                continue
            installment_ids = []
            for index in range(12):
                installment_ids.append((0, 0, {
                    "date": self.first_charge_date + relativedelta(months=index)
                }))
            plan.installment_ids = installment_ids
    
    def get_overlapping_plans(self):
        self.ensure_one()
        return self.search([
            "&", ("category_id","=",self.category_id.id),
            "&", ("grade_level_ids","in",self.grade_level_ids.ids),
            "|", ("fiscal_year_date_from","=",self.fiscal_year_date_from),
                 ("fiscal_year_date_to","=",self.fiscal_year_date_to)
        ])
    
    def _compute_default_partner_ids(self):
        for plan in self:
            result = []
            if plan.default:
                overlapping_plans = plan.get_overlapping_plans()
                students = self.env["res.partner"].search([
                    ("person_type","=","student"),
                    ("tuition_plan_ids","not in",overlapping_plans.ids),
                    ("grade_level_id","in",plan.grade_level_ids.ids)
                ])
                result = students.ids
            plan.default_partner_ids = result