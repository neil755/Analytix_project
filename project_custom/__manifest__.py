# -*- coding: utf-8 -*-
{
    'name': "project_custom",

    'summary': "Requirement List, TB, PRO Contact List",

    'description': """
Requirement List,TB customization and PRO Contact List 
    """,

    'author': "Neil",
    'website': "https://github.com/neil755",

    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['project', 'utm', 'prodiz_project_customization', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/tb.xml',
        'views/pro.xml',
    ],

    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
