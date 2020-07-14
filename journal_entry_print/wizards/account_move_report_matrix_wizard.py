# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMoveReportMatrixWizard(models.TransientModel):
    _name = "account.move.report.matrix.wizard"

    group_by_journal = fields.Boolean(string="Group by Journal")

    def action_confirm(self):
        active_ids = self.env.context.get("active_ids", [])
        datas = {
            "ids": active_ids,
            "model": "account.move",
            "form": self.read()[0]
        }

        return self.env.ref("journal_entry_print.action_account_move_report_matrix").report_action([], data=datas)