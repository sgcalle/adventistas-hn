# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderPayment(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = "sale.order.payment"
    _rec_name = "id"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    account_payment_id = fields.Many2one(comodel_name="account.payment")
    partner_id = fields.Many2one(comodel_name="res.partner")
    currency_id = fields.Many2one(comodel_name="res.currency")
    journal_id = fields.Many2one(string="Journal",
                                comodel_name="account.journal")
    reconciled_payment_ids = fields.One2many(string="Reconciled Payments",
                                            inverse_name="payment_id",
                                            comodel_name="sale.order.payment.reconcile")
    payment_date = fields.Date(string="Date", 
                                default=lambda _: fields.Date.today())
    memo = fields.Char(string="Memo")
    amount_paid = fields.Monetary(string="Amount Paid")
    reconcilable_amount = fields.Monetary(string="Reconcilable Amount",
                                            compute="_compute_reconcilable_amount")

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends("reconciled_payment_ids", "amount_paid")
    def _compute_reconcilable_amount(self):
        for record in self:
            amount = record.amount_paid

            for reconciled_payment in record.reconciled_payment_ids:
                amount -= reconciled_payment.amount_reconciled

            record.reconcilable_amount = amount

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################
    def action_reconcile(self):
        # ! Needs 'sale_order_id' in context.
        
        return {
            "name": "Sale Order Reconcile Payment Wizard",
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
            "res_model": "sale.order.reconcile.payment.wizard",
            "type": "ir.actions.act_window",
            "domain": "[]",
            "context": {
                "default_sale_order_id": self.env.context.get("sale_order_id"),
                "default_payment_id": self.id,
                "default_amount_to_reconcile": self.reconcilable_amount
            }
        }

    ####################
    # Business methods #
    ####################