# -*- coding: utf-8 -*-
{
    'name': "Tracker",

    'summary': "In Project - Audit Tracker",

    'description': """Overall Tracker""",

    'author': "Neil",
    'website': "https://github.com/neil755",

    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['project', 'sale_project', 'utm', 'prodiz_project_customization', 'sale', 'project_custom'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/audit_tracker.xml',


    ],

    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
