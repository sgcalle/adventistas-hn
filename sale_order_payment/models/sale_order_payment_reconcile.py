# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderPaymentReconcile(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = "sale.order.payment.reconcile"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    currency_id = fields.Many2one(string="Currency",
        comodel_name="res.currency")
    sale_order_id = fields.Many2one(string="Sale Order",
        require=True,
        ondelete="cascade",
        comodel_name="sale.order")
    payment_id = fields.Many2one(string="Payment",
        require=True,
        ondelete="cascade",
        comodel_name="sale.order.payment")
    amount_reconciled = fields.Monetary(string="Amount Reconciled")
    date_reconciled = fields.Date(string="Date", 
        default=lambda _: fields.Date.today(),
        required=True)

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################
    @api.model
    def create(self, vals):
        res = super(SaleOrderPaymentReconcile, self).create(vals)

        for record in res:
            so = record.sale_order_id

            if self.env.company.create_invoice_on_so_fully_paid_enabled and so.amount_due_after_reconcile <= 0:
                invoice = record.sale_order_id._create_invoices()
                so._create_invoice_with_reconciliation(invoice_id=invoice.id)
    
    ##################
    # Action methods #
    ##################
    def action_unreconcile(self):
        for record in self:
            record.unlink()

    ####################
    # Business methods #
    ####################