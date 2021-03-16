# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

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
    state = fields.Selection(string="State",
        selection=[("valid", "Valid"), ("cancelled", "Cancelled")],
        default="valid")
    account_payment_id = fields.Many2one(string="Related Invoice Payment",
        comodel_name="account.payment")
    partner_id = fields.Many2one(string="Customer",
        comodel_name="res.partner")
    currency_id = fields.Many2one(string="Currency",
        comodel_name="res.currency")
    journal_id = fields.Many2one(string="Journal",
        comodel_name="account.journal",
        domain="[('type','in',['bank','cash'])]")
    reconciled_payment_ids = fields.One2many(string="Reconciliations",
        inverse_name="payment_id",
        comodel_name="sale.order.payment.reconcile")
    payment_date = fields.Date(string="Date", 
        default=lambda _: fields.Date.today(),
        required=True)
    memo = fields.Char(string="Memo")
    amount_paid = fields.Monetary(string="Amount Paid")
    reconcilable_amount = fields.Monetary(string="Reconcilable Amount",
        compute="_compute_reconcilable_amount",
        store=True)

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
        wizard_obj = self.env["sale.order.reconcile.payment.wizard"]
        wizard = wizard_obj.create({
            "sale_order_id": self.env.context.get("sale_order_id"),
            "payment_id": self.id,
            "amount_to_reconcile": self.reconcilable_amount
        })

        return {
            "name": "Sales Order Reconcile Payment Wizard",
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
            "res_model": "sale.order.reconcile.payment.wizard",
            "type": "ir.actions.act_window",
            "domain": "[]",
            "res_id": wizard.id,
        }

    def action_cancel(self):
        self.ensure_one()
        if self.account_payment_id:
            raise ValidationError("You can't cancel a sales order payment with a related invoice payment.")
        self.state = "cancelled"
        self.reconciled_payment_ids.unlink()

    def action_reset_to_valid(self):
        self.ensure_one()
        self.state = "valid"

    ####################
    # Business methods #
    ####################