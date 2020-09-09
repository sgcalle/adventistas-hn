# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class Settings(models.TransientModel):
    """ Setting for surcharge """
    _inherit = "res.config.settings"

    pos_pr_surcharge_product_id = fields.Many2one("product.product",
                                                  string="Surcharge Product",
                                                  config_parameter='pos_pr.surcharge_product_id',
                                                  default=lambda record: record.env.ref('pos_pr.default_surcharge_product'),
                                                  )

    pos_pr_discount_product_id = fields.Many2one("product.product",
                                                 string="Discount Product",
                                                 config_parameter='pos_pr.discount_product_id',
                                                 default=lambda record: record.env.ref('pos_pr.default_discount_product'),
                                                 )

    pos_pr_surcharge_default_amount = fields.Float(config_parameter='pos_pr.surcharge_default_amount')
    pos_pr_discount_default_account_id = fields.Many2one('account.account', string="Default discount account",
                                                         config_parameter='pos_pr.discount_default_account_id')
