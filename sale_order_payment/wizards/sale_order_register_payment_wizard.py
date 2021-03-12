# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderRegisterPaymentWizard(models.TransientModel):
    ######################
    # Private attributes #
    ######################
    _name = "sale.order.register.payment.wizard"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    partner_id = fields.Many2one(comodel_name="res.partner")
    sale_order_id = fields.Many2one(comodel_name="sale.order")
    payment_date = fields.Date(string="Date", 
                                default=lambda _: fields.Date.today())
    amount_to_pay = fields.Float(string="Amount to Pay",
                                required=True)
    journal_id = fields.Many2one(string="Journal",
                                comodel_name="account.journal",
                                required=True,
                                domain=[("type", "=", "bank")])
    memo = fields.Char(string="Memo")

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################
    @api.constrains("amount_to_pay")
    def _check_amount_to_pay(self):
        for record in self:
            if record.amount_to_pay <= 0:
                raise ValidationError("Amount to Pay should not be 0.")

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################
    def action_register_sale_order_payment(self):
        self.ensure_one()

        so_payment_reconcile_obj = self.env["sale.order.payment.reconcile"]
        so_payment_obj = self.env["sale.order.payment"]

        amount_to_reconcile = self.sale_order_id.amount_total \
                                if self.amount_to_pay >= self.sale_order_id.amount_total else \
                                self.amount_to_pay

        so_payment = so_payment_obj.create({
            "partner_id": self.partner_id.id,
            "journal_id": self.journal_id.id,
            "payment_date": self.payment_date,
            "memo": self.memo,
            "amount_paid": self.amount_to_pay
        })

        so_payment_reconcile_obj.create({
            "sale_order_id": self.sale_order_id.id,
            "amount_reconciled": amount_to_reconcile,
            "date_reconciled": self.payment_date,
            "payment_id": so_payment.id
        })


    ####################
    # Business methods #
    ####################