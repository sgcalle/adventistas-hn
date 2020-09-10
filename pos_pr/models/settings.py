# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models, SUPERUSER_ID, exceptions

_logger = logging.getLogger(__name__)


def default_settings_values(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    default_surcharge_product_id = env['product.product']
    default_discount_product_id = env['product.product']

    try:
        default_surcharge_product_id = env.ref('pos_pr.default_surcharge_product')
        default_discount_product_id = env.ref('pos_pr.default_discount_product')
    except ValueError as e:
        _logger.error(e)

    env['ir.config_parameter'].set_param('pos_pr.surcharge_product_id', default_surcharge_product_id.id or '')
    env['ir.config_parameter'].set_param('pos_pr.discount_product_id', default_discount_product_id.id or '')


class Settings(models.TransientModel):
    """ Setting for surcharge """
    _inherit = "res.config.settings"

    pos_pr_surcharge_product_id = fields.Many2one("product.product", string="Surcharge Product",
                                                  config_parameter='pos_pr.surcharge_product_id')

    pos_pr_discount_product_id = fields.Many2one("product.product", string="Discount Product",
                                                 config_parameter='pos_pr.discount_product_id',)

    pos_pr_surcharge_default_amount = fields.Float(config_parameter='pos_pr.surcharge_default_amount')
    pos_pr_discount_default_account_id = fields.Many2one('account.account', string="Default discount account",
                                                         config_parameter='pos_pr.discount_default_account_id')
