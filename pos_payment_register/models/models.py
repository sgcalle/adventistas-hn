# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = "res.company"

    surcharge_amount = fields.Monetary()


class AccountJournal(models.Model):
    _inherit = "account.journal"

    surcharge_amount = fields.Monetary()


class PaymentGroup(models.Model):
    _name = "pos_payment_register.payment_group"

    account_payment_ids = fields.One2many("account.payment", "payment_group_id", string="Payments")
