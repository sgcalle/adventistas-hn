# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class PaymentGroup(models.Model):
    """ This payment group is used for reports """
    _name = "pos_pr.payment_group"

    account_payment_ids = fields.One2many("account.payment", "payment_group_id", string="Payments")
