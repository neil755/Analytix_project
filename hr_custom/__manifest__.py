# -*- coding: utf-8 -*-
{
    'name': "hr_custom",

    'summary': "HR Module Customization",

    'description': """
Addition of multiple fields 
    """,

    'author': "Neil Antony Pinheiro",
    'website': "https://github.com/neil755",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_recruitment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
