# -*- coding: utf-8 -*-
{
    'name': 'Payroll Accounting Extensions',

    'summary': """ Payroll Accounting Extensions """,

    'description': """
        Payroll Accounting Extensions
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Payroll',
    'version': '0.1',

    'depends': [
        'hr_payroll_account',
        'hr_payroll_extends',
    ],

    'data': [
        'views/hr_contract_views.xml',
        'views/hr_loan_views.xml',
        'views/hr_savings_views.xml',
    ],
}