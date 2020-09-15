# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class PaymentGroup(models.Model):
    """ This payment group is used for reports """
    _name = "pos_pr.payment_group"
    _description = 'Payments groups'

    name = fields.Char(string='Name')
    invoice_payment_ids = fields.One2many("pos_pr.invoice.payment", "payment_group_id", string="Payments")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals:
                vals['name'] = self.env['ir.sequence'].next_by_code('seq.pos.payment.register.invoice.payment_group')
        return super().create(vals_list)
