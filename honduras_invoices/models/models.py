# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    prefix = fields.Char("Prefix")

    authorized_range_from = fields.Integer("Authorized range from")
    authorized_range_to = fields.Integer("Authorized range to")

    cai = fields.Char("CAI")
    issue_limit_date = fields.Date("Issue limit date")

    def write(self, values):
        for record in self:

            sequence_write = {}

            if "prefix" in values:
                sequence_write["prefix"] = values["prefix"]

            if "authorized_range_from" in values:
                sequence_write["number_next"] = values["authorized_range_from"]

            sequence_write["use_date_range"] = False

            if sequence_write:
                self.sequence_id.write(sequence_write)
        return super().write(values)

    @api.onchange("prefix")
    def _onchange_prefix(self):
        for record in self:
            record.sequence_id.prefix = record.prefix

    @api.onchange("authorized_range_from")
    def _onchange_prefix(self):
        for record in self:
            record.sequence_id.number_next = record.authorized_range_from

    @api.onchange("authorized_range_to")
    def _onchange_prefix(self):
        pass
#        Maybe we can do something like this?.
#        for record in self:
#            record.sequence_id.max_numnber = record.authorized_range_to
