# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderReconcilePaymentWizard(models.TransientModel):
    ######################
    # Private attributes #
    ######################
    _name = "sale.order.reconcile.payment.wizard"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    sale_order_id = fields.Many2one(string="Sale Order",
        comodel_name="sale.order")
    payment_id = fields.Many2one(string="Payment Record",
        comodel_name="sale.order.payment")
    amount_to_reconcile = fields.Float(string="Amount to Pay",
        required=True)
    date_reconciled = fields.Date(string="Date", 
        default=lambda _: fields.Date.today())

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################
    @api.constrains("amount_to_reconcile")
    def _check_amount_to_pay(self):
        for record in self:
            if record.amount_to_reconcile <= 0:
                raise ValidationError("Amount to Reconcile should not be 0.")

            # if record.amount_to_reconcile > record.sale_order_id.amount_total:
            #     raise ValidationError("Amount to Reconcile is greater than the Sale Order's total!")

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################
    def action_reconcile_payment(self):
        self.ensure_one()

        so_payment_reconcile_obj = self.env["sale.order.payment.reconcile"]

        amount_to_reconcile = self.sale_order_id.amount_due_after_reconcile \
                                if self.amount_to_reconcile > self.sale_order_id.amount_due_after_reconcile \
                                else self.amount_to_reconcile

        if amount_to_reconcile > 0:
            so_payment_reconcile_obj.create({
                "sale_order_id": self.sale_order_id.id,
                "payment_id": self.payment_id.id,
                "amount_reconciled": amount_to_reconcile,
                "date_reconciled": self.date_reconciled
            })

    ####################
    # Business methods #
    ####################