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
    """ This modify the default sale order behaviour """
    _inherit = "sale.order"

    journal_id = fields.Many2one("account.journal", string="Journal", domain="[('type', '=', 'sale')]")
    
    # Invoice Date
    invoice_date_due = fields.Datetime(string='Due Date')
    invoice_date = fields.Datetime(string='Invoice Date')

    # School fields
    student_id = fields.Many2one("res.partner", string="Student", domain=[('person_type', '=', 'student')])
    family_id = fields.Many2one("res.partner", string="Family", domain=[('is_family', '=', True)])

    def _create_invoices(self, grouped=False, final=False):
        all_moves = super()._create_invoices(grouped, final)

        receivable_behaviour = self.env["ir.config_parameter"].sudo().get_param('school_finance.receivable_behaviour')

        for order in self:
            # Basically, we change the move_ids receivable account to student if the settings allow it
            if receivable_behaviour == 'student' and order.student_id.person_type == 'student':

                # We find the line with receivable
                receivable_lines = order.invoice_ids.line_ids.filtered(
                    lambda line: line.account_id.internal_type == 'receivable')

                # And force them to change :P
                receivable_lines.sudo().write({
                    "account_id": order.student_id.property_account_receivable_id.id
                })

            # Update values
            write_variables = dict()

            if order.journal_id:
                write_variables["journal_id"] = order.journal_id.id
            
            if order.invoice_date:
                write_variables["invoice_date"] = order.invoice_date
                write_variables["date"] = order.invoice_date

            if order.payment_term_id or order.invoice_date_due:
                # If there is an invoice that already has payment terms, we will recompute the payment terms...
                invoice_ids_with_payment_terms = order.invoice_ids.filtered("invoice_payment_term_id")
                invoice_ids_with_payment_terms._recompute_payment_terms_lines()

                # The rest of the invoices we are going to just write the invoice date due
                (order.invoice_ids - invoice_ids_with_payment_terms).write({"invoice_date_due": order.invoice_date_due})

            if order.student_id:
                write_variables["student_id"] = order.student_id.id
                write_variables["student_grade_level"] = order.student_id.grade_level_id.id
                write_variables["student_homeroom"] = order.student_id.homeroom

            if order.family_id:
                write_variables["family_id"] = order.family_id.id

            if write_variables:
                order.invoice_ids.write(write_variables)
        
        return all_moves
        
        
class SaleOrderLine(models.Model):
    """ Sale Order Line """
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
        