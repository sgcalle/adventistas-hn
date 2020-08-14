# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrPayslipReportSummaryXlsx(models.AbstractModel):
    _name = "report.hr_payroll_reports.hr_payslip_report_summary_xlsx"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        header_format = workbook.add_format({"font_size":14, "align": "vcenter", "bold": True})
        sheet = workbook.add_worksheet("Tax Report")

        sheet.write(0, 0, "Customer Tax ID", header_format)
        sheet.write(0, 1, "Customer Name", header_format)
        sheet.write(0, 2, "Date Paid", header_format)
        sheet.write(0, 3, "Untaxed Amount", header_format)
        sheet.write(0, 4, "Tax Amount", header_format)
        sheet.write(0, 5, "Total Paid", header_format)