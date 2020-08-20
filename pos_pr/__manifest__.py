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
    'category': 'Sales/Point Of Sale',
    'version': '1.1-beta',


    # any module necessary for this one to work correctly
    'depends': ['base',
                'point_of_sale',
                'school_base',
                'school_finance'],

    'data': [
        'security/ir.model.access.csv',

        'data/surcharge_product.xml',
        'data/assets.xml',
        'data/sequence.xml',

        'views/invoice_payment_views_and_menus.xml',

        'views/inherited/point_of_save_views.xml',
        'views/inherited/account_journal_views.xml',
        'views/inherited/cash_control_views.xml',

        'views/settings_view.xml',
    ],

    'qweb': [
        'static/src/xml/pos_view.xml'
    ],

}
