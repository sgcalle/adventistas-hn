# -*- coding: utf-8 -*-
{
    'name': 'Honduras POS Payment Register',

    'summary': """ Honduras POS Payment Register """,

    'description': """
        Honduras POS Payment Register
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Point of Sale',
    'version': '1.0',

    'depends': [
        'pos_pr',
        'honduras_invoices',
    ],

    'data': [
        'reports/pos_pr_invoice_payment_report_templates.xml',
        'reports/pos_pr_invoice_payment_reports.xml',
        'wizards/pos_pr_invoice_payment_report_wizard_views.xml',
    ],
}