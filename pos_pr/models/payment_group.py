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
    payment_amount_total = fields.Monetary()
    payment_change = fields.Monetary()

    partner_id = fields.Many2one('res.partner', required=True)
    date = fields.Datetime()

    pos_session_id = fields.Many2one('pos.session', required=True)
    currency_id = fields.Many2one('res.currency', related='pos_session_id.currency_id')

    @api.model
    def create(self, vals):
        if 'name' not in vals:
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.pos.payment.register.invoice.payment_group')
        if 'date' not in vals:
            vals['date'] = fields.Datetime.to_string(fields.Datetime.now())

        # payment_change = vals.get('payment_change', 0)
        # if payment_change:
        #     invoice_payment_ids = vals.get('invoice_payment_ids', [])
        #
        #     cash_id = self.env['pos.session'].browse(vals['pos_session_id']).payment_method_ids.filtered('is_cash_count')[:1]
        #
        #     invoice_payment_ids.append([0, 0, {
        #         'date': vals['date'],
        #         'partner_id': vals.get('partner_id', False),
        #         'invoice_address_id': vals.get('partner_id', False),
        #         'payment_amount': -payment_change,
        #         'payment_method_id': cash_id.id,
        #         'pos_session_id': vals['pos_session_id'],
        #         # 'move_id': '',
        #     }])
        #     vals['invoice_payment_ids'] = invoice_payment_ids

        return super().create(vals)
