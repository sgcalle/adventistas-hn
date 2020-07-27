# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class PaymentGroup(models.Model):
    _name = "pos_payment_register.payment_group"

    account_payment_ids = fields.One2many("account.payment", "payment_group_id", string="Payments")
