# -*- coding: utf-8 -*-
{
    'name': "school_base",

    'summary': """
        Common models for eduwebgroup school modules as School Year, Grade Level, etc...""",

    'description': """
        Common models for eduwebgroup school modules
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'School',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/menudata.xml',
        'views/res_partner_view.xml',
        'views/views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}