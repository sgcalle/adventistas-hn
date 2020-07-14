# -*- coding: utf-8 -*-

from dateutil import parser
from pytz import timezone, utc

from odoo import models, fields, api

class AccountMoveReportMatrix(models.AbstractModel):
    _name = "report.journal_entry_print.account_move_report_matrix"

    @api.model
    def _get_report_values(self, docids, data=None):
        move_ids = self.env.context.get("active_ids", [])
        moves = self.env["account.move"].browse(move_ids)
        
        journals = self.env["account.journal"]
        if data["form"]["group_by_journal"]:
            for move in moves:
                journals |= move.journal_id

        return {
            "doc_ids": move_ids,
            "doc_model": "account.move",
            "docs": moves,
            "data": data,
            "journals": journals,
        }