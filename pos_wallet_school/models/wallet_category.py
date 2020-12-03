# -*- coding: utf-8 -*-

import logging
from odoo import models

logger = logging.getLogger(__name__)


class WalletCategory(models.Model):
    _inherit = 'wallet.category'

    def get_wallet_amount(self, partner_id, wallet_category_id=False):
        wallet_amount = super(WalletCategory, self).get_wallet_amount(partner_id, wallet_category_id)

        partner_id, wallet_category_id = self._parse_get_wallet_amount_params(partner_id, wallet_category_id)

        if partner_id.person_type == 'student':
            wallet_amount -= sum(self.env['pos.payment'].search([
                ('payment_method_id', '=', wallet_category_id.pos_payment_method_id.id),
                ('student_id', '=', partner_id.id),
                ]).mapped('amount'))
        elif partner_id.is_family:
            wallet_amount -= sum(self.env['pos.payment'].search([
                ('payment_method_id', '=', wallet_category_id.pos_payment_method_id.id),
                ('family_id', '=', partner_id.id),
                ]).mapped('amount'))

        return wallet_amount
