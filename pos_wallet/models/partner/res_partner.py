# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import ValidationError
import json
import typing

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pos_session_wallet_load_ids = fields.One2many('pos_wallet.wallet.load', 'partner_id')
    pos_session_wallet_payment_ids = fields.One2many('pos_wallet.wallet.payment', 'partner_id')

    @api.depends('invoice_ids', 'pos_session_wallet_load_ids', 'pos_session_wallet_payment_ids', 'pos_order_ids')
    def _compute_json_dict_wallet_amounts(self):
        super(ResPartner, self)._compute_json_dict_wallet_amounts()

    def get_wallet_balances_dict(self, wallet_id_list: typing.List[int]) -> dict:
        wallet_balances_dict = super().get_wallet_balances_dict(wallet_id_list)

        for wallet_id, balance in wallet_balances_dict.items():
            wallet_loads = self.pos_session_wallet_load_ids.filtered(
                lambda wallet_load: wallet_load.pos_session_id.state in ['opened', 'closing_control'] and wallet_load.wallet_category_id.id == wallet_id)
            wallet_payments = self.pos_session_wallet_payment_ids.filtered(
                lambda wallet_payment: wallet_payment.pos_session_id.state in ['opened', 'closing_control'] and wallet_payment.wallet_category_id.id == wallet_id)

            real_final_balance = balance + sum(wallet_loads.mapped('amount')) - sum(wallet_payments.mapped('amount'))
            wallet_balances_dict[wallet_id] = real_final_balance

        return wallet_balances_dict
