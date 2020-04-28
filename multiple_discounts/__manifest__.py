# -*- coding: utf-8 -*-
{
    'name': "Multiple Discounts",

    'summary': """ Add multiple discount to sale """,

    'description': """ Auto discounts to partner by sale orders """,

    'author': "Eduwebgroup",
    'website': "http://www.eduwebgroup.com",
    
    'category': 'accounting',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
}
