# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class SaleOrderForStudents(models.Model):
    _inherit = "sale.order"

    journal_id = fields.Many2one("account.journal", string="Journal", domain="[('type', '=', 'sale')]")
    
    # Invoice Date
    invoice_date_due = fields.Datetime(string='Due Date')
    invoice_date     = fields.Datetime(string='Invoice Date')

    #School fields
    student_id = fields.Many2one("res.partner", string="Student", domain=[('person_type', '=', 'student')])
    family_id = fields.Many2one("res.partner", string="Family", domain=[('is_family', '=', True)])

    def _prepare_invoice(self):
        self.ensure_one()
        invoice_vals = super(SaleOrderForStudents, self)._prepare_invoice()
        if self.invoice_date:
            invoice_vals["invoice_date"] = self.invoice_date
        if self.invoice_date_due:
            invoice_vals["invoice_date_due"] = self.invoice_date_due
        if self.student_id:
            invoice_vals["student_id"] = self.student_id.id
        if self.family_id:
            invoice_vals["family_id"] = self.family_id.id
        if self.journal_id:
            invoice_vals["journal_id"] = self.journal_id.id
        return invoice_vals

    def _create_invoices(self, grouped=False, final=False):

        all_moves = super()._create_invoices(grouped, final)

        receivable_behaviour = self.env["ir.config_parameter"].get_param('school_finance.receivable_behaviour')

        for order in self:
            if receivable_behaviour == 'student' and order.partner_id.person_type == 'student':
                receivable_lines = order.invoice_ids.line_ids.filtered(lambda line: line.account_id.internal_type == 'receivable')
                receivable_lines.sudo().write({
                    "account_id": order.partner_id.property_account_receivable_id.id
                })
        
        return all_moves
        
        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        super().product_uom_change()
        if not self.order_id.pricelist_id and not self.order_id.partner_id:
            self.price_unit = self.product_id.lst_price

    @api.onchange('product_id')
    def product_id_change(self):
        res = super().product_id_change()

        if not self.order_id.pricelist_id and not self.order_id.partner_id:
            price_unit = self.product_id.lst_price
            self.write({"price_unit": price_unit})
        
        return res
        