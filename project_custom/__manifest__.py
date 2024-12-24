# -*- coding: utf-8 -*-
{
    'name': "project_custom",

    'summary': "Requirement List and TB",

    'description': """
Requirement List and TB customization
    """,

    'author': "Neil Antony",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'utm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/tb.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
