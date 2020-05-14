# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _


class ResPartnerMakeSale(models.TransientModel):
    _name = "res.partner.make.sale"
    _description = "Make a sale for a partner"
    order_line_ids = fields.Many2many(
        "sale.order.line", string="Order Lines", ondelete="cascade")
    journal_id = fields.Many2one("account.journal", string="Journal", domain=[
                                 ("type", "=", "sale")])
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                          check_company=True,  # Unrequired company
                                          domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                          help="The analytic account related to a sales order.")

    # Invoice Date
    invoice_date_due = fields.Datetime(string='Due Date')
    invoice_date = fields.Datetime(string='Invoice Date')

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
                                   domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                   help="If you change the pricelist, only newly added lines will be affected.")

    @api.model
    def create(self, values):
        if type(values) == dict and "order_line_ids" in values:
            partner_ids = self.env["res.partner"].browse(
                self.env.context.get("active_ids", []))

            SaleOrderEnv = self.env["sale.order"]
            sales = self.env["sale.order"]
            for partner_id in partner_ids:


                partner_pricelist = partner_id.property_product_pricelist and partner_id.property_product_pricelist.id or False
                pricelist_id = values.setdefault("pricelist_id", False)

                sale_pricelist = pricelist_id if pricelist_id else partner_pricelist

                sales = sales + SaleOrderEnv.create({
                    "date_order": datetime.now(),
                    "partner_id": partner_id.id,
                    "analytic_account_id": values["analytic_account_id"],
                    "journal_id": values["journal_id"],
                    "order_line": values["order_line_ids"],
                    "invoice_date": values["invoice_date"],
                    "invoice_date_due": values["invoice_date_due"],
                    "pricelist_id": sale_pricelist,
                })

            # We need to stop order_lines from being created
            # because it give us error, it needs a sale.order to be created
            del values["order_line_ids"]
        return super().create({})  # {'type': 'ir.actions.act_window_close'}
