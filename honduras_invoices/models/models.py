# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

# raise UserError(_('There is no responsible family for %s') % (line.product_id.categ_id.name))

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    prefix = fields.Char("Prefix")

    is_honduras_invoice = fields.Boolean()

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

            if ("is_honduras_invoice" in values and values["is_honduras_invoice"]) or ("is_honduras_invoice" not in values and record.is_honduras_invoice):
                # Check for every new field
                
                prefix                = values["prefix"] if "prefix" in values else record.prefix
                authorized_range_from = values["authorized_range_from"] if "authorized_range_from" in values else record.authorized_range_from
                authorized_range_to   = values["authorized_range_to"] if "authorized_range_to" in values else record.authorized_range_to
                cai                   = values["cai"] if "cai" in values else record.cai
                issue_limit_date      = values["issue_limit_date"] if "issue_limit_date" in values else record.issue_limit_date 
                
                if not prefix:
                    raise UserError(_('Prefix is not set'))
                if not authorized_range_from:
                    raise UserError(_('Authorized range from is not set'))
                if not authorized_range_to:
                    raise UserError(_('Authorized range to is not set'))
                if not cai:
                    raise UserError(_('CAI is not set'))
                if not issue_limit_date:
                    raise UserError(_('Issue limit date is not set'))
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
