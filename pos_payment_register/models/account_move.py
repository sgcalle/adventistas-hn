# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    """ Added some field to easier point of sale javascript """
    _inherit = "account.move"

    surcharge_invoice_id = fields.Many2one("account.move", "Surcharge Invoice")
    is_overdue = fields.Boolean(compute="_compute_is_overdue", default=False)
    is_overdue_stored = fields.Boolean(compute="_compute_is_overdue_stored", store=True, default=False)

    def _compute_is_overdue(self):
        for move_id in self:
            today = datetime.today()

            if move_id.invoice_date_due:
                move_id.is_overdue = move_id.invoice_date_due < today.date()
            else:
                move_id.is_overdue = False

    @api.depends("is_overdue")
    def _compute_is_overdue_stored(self):
        for move_id in self:
            move_id.is_overdue_stored = move_id.is_overdue
