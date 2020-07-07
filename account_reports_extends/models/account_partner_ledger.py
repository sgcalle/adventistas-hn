# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"

    @api.model
    def _do_query(self, options, expanded_partner=None):
        res = super(AccountPartnerLedger, self)._do_query(options, expanded_partner=expanded_partner)
        new_res = []
        for partner, result in res:
            if result.get("lines"):
                result["lines"] = sorted(result["lines"], key=lambda l: (l["date"], l["id"]))
            new_res.append((partner, result))
        return new_res