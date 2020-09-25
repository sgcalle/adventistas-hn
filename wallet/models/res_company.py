# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    default_wallet_account_id = fields.Many2one("account.account", string='Default wallet account')
    default_wallet_credit_limit = fields.Float(string='Wallet credit limit')