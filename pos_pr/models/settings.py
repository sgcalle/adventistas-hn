# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class Settings(models.TransientModel):
    """ Setting for surcharge """
    _inherit = "res.config.settings"

    surcharge_product_id = fields.Many2one("product.product",
                                           string="Surcharge Product",
                                           config_parameter='pos_pr.surcharge_product_id',
                                           # default=lambda record: record.env.ref('pos_pr.surcharge_product'),
                                           )

    surcharge_default_amount = fields.Float(config_parameter='pos_pr.surcharge_default_amount')
