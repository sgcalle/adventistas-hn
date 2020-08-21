# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class WalletSettings(models.TransientModel):
    _inherit = "res.config.settings"

    wallet_default_account_id = fields.Many2one("account.account",
                            string='Default wallet account',
                            config_parameter='wallet.default_account_id')

    wallet_credit_limit = fields.Float(string='Wallet credit limit',
                                          config_parameter='wallet.wallet_credit_limit',
                                          default=0.0)

    def execute(self):
        _logger.info("Updating default wallet account: %s" % (self.wallet_default_account_id.name_get()))

        default_wallet_product_id = self.env.ref("wallet.product_default_wallets")
        default_wallet_id = self.env.ref("wallet.default_wallet_category")
        default_wallet_product_id.property_account_income_id = False

        account_id = self.wallet_default_account_id

        default_wallet_product_id.write({"property_account_income_id": account_id})
        default_wallet_id.write({"account_id": account_id})
        return super().execute()
