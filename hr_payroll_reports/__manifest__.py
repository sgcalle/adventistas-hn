# -*- coding: utf-8 -*-
{
    'name': 'Payroll Reports',

    'summary': """ Payroll Reports """,

    'description': """
        Payroll Reports
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Payroll',
    'version': '1.0',

    'depends': [
        'hr_payroll',
        'report_xlsx',
    ],

    'data': [
        'reports/hr_payslip_reports.xml',
        'wizards/hr_payslip_report_summary_xlsx_wizard_views.xml',
    ],
}