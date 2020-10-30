# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import fields, models, api, _, exceptions


class PosSession(models.Model):
    _inherit = "pos.session"

    pos_wallet_load_ids = fields.One2many('pos_wallet.wallet.load', 'pos_session_id')
    pos_wallet_payment_ids = fields.One2many('pos_wallet.wallet.payment', 'pos_session_id')

    pos_wallet_loads_amount = fields.Float(compute='_compute_cash_balance', store=True)
    pos_wallet_payments_amount = fields.Float(compute='_compute_cash_balance', store=True)

    def _validate_session(self):
        action = super()._validate_session()

        if self.pos_wallet_load_ids:
            self.pos_wallet_load_ids.apply_loads()

        return action

    def _compute_cash_balance(self):
        super()._compute_cash_balance()
        for session in self:
            session.pos_wallet_loads_amount = sum(session.pos_wallet_load_ids.mapped('amount'))
            session.pos_wallet_payments_amount = sum(session.pos_wallet_payment_ids.mapped('amount'))

            session.cash_register_total_entry_encoding += sum(session.pos_wallet_load_ids.filtered('payment_method_id.is_cash_count').mapped('amount'))

    @api.model
    def get_partner_receivable(self, partner_id):
        return self.env['res.partner'].browse(partner_id).property_account_receivable_id

