# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

DEFAULT_FIELDS = [
    "hr_payroll.field_hr_employee__registration_number",
    "hr.field_hr_employee__name",
    "hr.field_hr_employee__job_id",
]

class HrPayslipXlsxReportSummaryXlsxWizard(models.TransientModel):
    _name = "hr.payslip.report.summary.xlsx.wizard"
    _description = "Payslip Summary Report Wizard"

    def _default_struct_ids(self):
        active_ids = self.env.context.get("active_ids", [])
        payslips = self.env["hr.payslip"].browse(active_ids)
        return payslips.mapped("struct_id").ids
    
    def _default_line_ids(self):
        res = []
        for index, field in enumerate(DEFAULT_FIELDS):
            res.append((0, 0, {
                "sequence": index,
                "type": "field",
                "field_id": self.env.ref(field)
            }))
        struct_id = self._default_struct_ids()[0]
        struct = self.env["hr.payroll.structure"].browse(struct_id)
        sequence = len(DEFAULT_FIELDS)
        for rule in struct.rule_ids:
            res.append((0, 0, {
                "sequence": sequence,
                "type": "rule",
                "rule_id": rule.id,
                "code": rule.code,
            }))
            sequence += 1
        return res

    grouping = fields.Selection(string="Group By",
        selection=[ 
            ('department', 'Department')],
        default='department')
    line_ids = fields.One2many(string="Lines",
        comodel_name="hr.payslip.report.summary.xlsx.wizard.line",
        inverse_name="wizard_id",
        default=_default_line_ids)
    struct_ids = fields.Many2many(string="Salary Structures",
        comodel_name="hr.payroll.structure",
        default=_default_struct_ids,
        readonly=True)

    def action_confirm(self):
        active_ids = self.env.context.get("active_ids", [])
        datas = {
            "ids": active_ids,
            "model": "hr.payslip",
            "form": self.read()[0]
        }
        return self.env.ref("hr_payroll_reports.action_hr_payslip_report_summary_xlsx").report_action([], data=datas)