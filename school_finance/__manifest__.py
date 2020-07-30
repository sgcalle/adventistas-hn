# -*- coding: utf-8 -*-
{
    'name': "School finances",

    'summary': """ Finance addons for schools """,

    'description': """ Finance addon """,

    'author': "Eduwebgroup",
    'website': "http://www.Eduwebgroup.com",

    'category': 'Invoicing',
    'version': '0.12',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'school_base',
        'sale',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        # Actions
        'data/sale_order_actions.xml',

        # Views
        'views/views.xml',
        'views/templates.xml',
        'views/config_views.xml',

        # Inherited views
        'views/inherited_views/product_category.xml',
        'views/inherited_views/account_journal.xml',

        # Wizards
        'wizard/res_partner_make_sale.xml',

    ],
}
