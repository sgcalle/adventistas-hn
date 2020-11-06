# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import json
import typing

logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    wallet_category_id = fields.Many2one('wallet.category')
    is_wallet_payment_method = fields.Boolean()


class WalletCategory(models.Model):
    _inherit = 'wallet.category'

    pos_payment_method_id = fields.Many2one('pos.payment.method', store=True, compute='_compute_pos_payment_method_id')

    @api.depends('name', 'account_id', 'company_id')
    def _compute_pos_payment_method_id(self):
        wallet_without_accounts = self.search([('account_id', '=', False)])
        if wallet_without_accounts:
            raise ValidationError(_('You need to set up an account to the next wallet before installing pos_wallet: %') %
                                  wallet_without_accounts.mapped(lambda wl: _('Wallet[%s]: %s, Company[%]: %s') % (wl.id, wl.name, wl.company_id.id, wl.company_id.name)))
        for wallet_category_id in self:
            if not wallet_category_id.pos_payment_method_id:
                wallet_category_id.pos_payment_method_id = self.env['pos.payment.method'].create({
                    'name': wallet_category_id.name,
                    'receivable_account_id': wallet_category_id.account_id.id,
                    'company_id': wallet_category_id.company_id.id,

                    'is_cash_count': False,
                    'wallet_category_id': wallet_category_id.id,
                    'is_wallet_payment_method': True,
                    'split_transactions': True,
                    })
            else:
                wallet_category_id.pos_payment_method_id.update({
                    'name': wallet_category_id.name,
                    'receivable_account_id': wallet_category_id.account_id.id,
                    'company_id': wallet_category_id.company_id.id,
                    })

    def get_wallet_amount(self, partner_id, wallet_category_id=False):
        wallet_amount = super(WalletCategory, self).get_wallet_amount(partner_id, wallet_category_id)

        if type(wallet_category_id) == int:
            wallet_category_id = self.env["wallet.category"].browse([wallet_category_id])
        elif not wallet_category_id:
            wallet_category_id = self

        if wallet_category_id:
            wallet_amount -= sum(self.env['pos.payment'].search([('payment_method_id', '=', wallet_category_id.pos_payment_method_id.id)]).mapped('amount'))

        return wallet_amount
