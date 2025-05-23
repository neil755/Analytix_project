# -*- coding: utf-8 -*-
{
    'name': "frontdesk",

    'summary': "Customer Data Entry",

    'description': """
Data entry for Customers that visit office directly
    """,

    'author': "Neil",
    'website': "https://github.com/neil755",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'utm'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',

    ],

    'installable': True,
    'auto_install': False,
    'application': True,

}
