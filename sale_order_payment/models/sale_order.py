# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = 'sale.order'

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    reconciled_payment_ids = fields.One2many(string="Reconciliations",
        inverse_name="sale_order_id",
        comodel_name="sale.order.payment.reconcile")
    reconciled_total = fields.Monetary(string="Total Reconciled Amount",
        compute="_compute_reconciled_total")
    reconcilable_payment_ids = fields.Many2many(string="Reconcilable Payments",
        compute="_compute_reconcilable_payment_ids",
        comodel_name="sale.order.payment")
    len_reconcilable_payment_ids = fields.Integer(compute="_compute_len_reconcilable_payment_ids",
        readonly=True)
    amount_due_after_reconcile = fields.Monetary(string="Amount Due",
        compute="_compute_amount_due_after_reconcile",
        readonly=True)
    payments_with_reconcile = fields.Many2many(readonly=True,
        compute="_compute_payments_with_reconcile",
        comodel_name="sale.order.payment")                    

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends("reconciled_payment_ids")
    def _compute_reconciled_total(self):
        for so in self:
            total = 0

            for reconciled_payment in so.reconciled_payment_ids:
                total += reconciled_payment.amount_reconciled

            so.reconciled_total = total

    def _compute_reconcilable_payment_ids(self):
        so_payment = self.env["sale.order.payment"]

        for so in self:
            so_payments = so_payment.search([
                ("state", "=", "valid"),
                ("partner_id", "=", so.partner_id.id),
                ("reconcilable_amount",">",0)]).ids

            if so_payments:
                so.reconcilable_payment_ids = [(6, 0, so_payments)]
            else:
                so.reconcilable_payment_ids = [(5, 0, 0)]

    @api.depends("reconcilable_payment_ids")
    def _compute_len_reconcilable_payment_ids(self):
        for so in self:
            so.len_reconcilable_payment_ids = len(so.reconcilable_payment_ids)

    @api.depends("reconciled_total", "amount_total")
    def _compute_amount_due_after_reconcile(self):
        for so in self:
            so.amount_due_after_reconcile = so.amount_total - so.reconciled_total

    def _compute_payments_with_reconcile(self):
        for so in self:
            payment_ids = [r.payment_id.id for r in so.reconciled_payment_ids]

            if payment_ids:
                so.payments_with_reconcile = [(6, 0, payment_ids)]
            else:
                so.payments_with_reconcile = [(5, 0, 0)]


    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################
    def action_sale_order_payment(self):
        return {
            "name": "Sales Order Payment Wizard",
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
            "res_model": "sale.order.register.payment.wizard",
            "type": "ir.actions.act_window",
            "domain": "[]",
            "context": {
                "default_amount_to_pay": self.amount_due_after_reconcile,
                "default_memo": self.name,
                "default_sale_order_id": self.id,
                "default_partner_id": self.partner_id.id
            }
        }

    def action_cancel(self):
        for payment in self.payments_with_reconcile:
            payment.action_cancel()

        return super(SaleOrder, self).action_cancel()

    ####################
    # Business methods #
    ####################
    def _create_invoice_with_reconciliation(self, invoice_id=None):
        self.ensure_one()

        account_move_obj = self.env["account.move"]
        account_payment_obj = self.env["account.payment"]
        manual_payment = self.env["account.payment.method"].search([
            ("name", "=", "Manual"), ("payment_type", "=", "inbound")])

        if invoice_id:
            # Automatic creation of invoice
            invoice = account_move_obj.browse(invoice_id)
        else:
            # From create invoice wizard
            invoice = self.invoice_ids[-1]

        if invoice.state == "draft":
            invoice.action_post()

        for payment in self.payments_with_reconcile:
            if payment.state == "valid":
                account_payment = payment.account_payment_id
                if not account_payment:
                    account_payment = account_payment_obj.create({
                        "payment_type": "inbound",
                        "partner_type": "customer",
                        "partner_id": self.partner_id.id,
                        "amount": payment.amount_paid,
                        "journal_id": payment.journal_id.id,
                        "payment_method_id": manual_payment.id
                    })
                    payment.update({
                        "account_payment_id": account_payment.id
                    })
                    account_payment.post()

                for line in account_payment.move_line_ids:
                    if line.account_internal_type == "receivable":
                        invoice.js_assign_outstanding_line(line.id)
