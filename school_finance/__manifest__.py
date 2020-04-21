# -*- coding: utf-8 -*-
{
    'name': "School finances",

    'summary': """ Finance addons for schools """,

    'description': """ Finance addon """,

    'author': "Eduwebgroup",
    'website': "http://www.Eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing',
    'version': '0.2.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'school_base',
        'sale',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizard/res_partner_make_sale.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
