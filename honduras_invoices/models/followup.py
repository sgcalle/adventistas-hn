# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class AccountFollowupReport(models.AbstractModel):
    _inherit = "account.followup.report"

    def _get_columns_name(self, options):
        """
        Override
        Return the name of the columns of the follow-ups report
        """
        headers = super()._get_columns_name(options)
        headers.append({'name': _('Student'), 'style': 'text-align:right; white-space:nowrap;'})
        #            {'name': _('Date2'), 'class': 'date', 'style': 'text-align:center; white-space:nowrap;'},
        #            {'name': _('Due Date2'), 'class': 'date', 'style': 'text-align:center; white-space:nowrap;'},
        #            {'name': _('Source Document2'), 'style': 'text-align:center; white-space:nowrap;'},
        #            {'name': _('Communication2'), 'style': 'text-align:right; white-space:nowrap;'},
        #            {'name': _('Expected Date2'), 'class': 'date', 'style': 'white-space:nowrap;'},
        #            {'name': _('Excluded2'), 'class': 'date', 'style': 'white-space:nowrap;'},
        #            {'name': _('Total Due2'), 'class': 'number o_price_total', 'style': 'text-align:right; white-space:nowrap;'}
        #           ]
        # if self.env.context.get('print_mode'):
        #     headers = headers[:5] + headers[7:]  # Remove the 'Expected Date' and 'Excluded' columns
        return headers

    def _get_lines(self, options, line_id=None):
        lines = super()._get_lines(options, line_id)

        student_ids = self.env["res.partner"]
        for line in lines:
            # line["unfoldable"] = line["unfolded"] = True
            if line.get("class", False):
                continue
            student_ids += line["account_move"].student_id
            student_name = line["account_move"].student_id.name
            line["columns"].append({"name": student_name})
        
        new_line = list()
        student_ids = list(set(student_ids))
        for student_id in student_ids:
            student_invoice_ids = list(filter(lambda line: "account_move" in line and line["account_move"].student_id == student_id, lines))
            new_line.append({
                "name": student_id.name,
                "level": 2,
                "unfoldable": not not student_invoice_ids,
                "id": student_id.id,
            })
            for student_invoice_id in student_invoice_ids:
                student_invoice_id["parent_id"] = student_id
                new_line.append(student_invoice_id)
        
        return new_line
