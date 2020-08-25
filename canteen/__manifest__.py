# -*- coding: utf-8 -*-
{
    'name': 'Canteen',

    'summary': """ Canteen """,

    'description': """
        Canteen
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Sales',
    'version': '1.0',

    'depends': [
        'account',
        'sale_management',
        'portal',
        'school_finance',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/product_template_views.xml',
        'views/canteen_order_portal_templates.xml',
        'data/ir_cron_data.xml',
    ],
}