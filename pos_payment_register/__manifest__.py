# -*- coding: utf-8 -*-
{
    'name': "POS Payment Register",

    'summary': """ Implements a payment register in POS """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Eduwebgroup",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    'qweb': [
        'static/src/xml/pos_view.xml'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        # Product
        'data/product/surcharge_product.xml',

        # Inherited views
        'views/inherited/account_journal_views.xml',

        'views/templates.xml',
        'views/settings_view.xml',
    ],
}
