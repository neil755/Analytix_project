# -*- coding: utf-8 -*-
{
    'name': "PRO Master File",

    'summary': "Master File",

    'description': """
Overall Master File
    """,

    'author': "Neil",
    'website': "https://github.com/neil755",

    'version': '17.0',

    'depends': ['base', 'sale', 'utm', 'contacts', 'crm', 'crm_modification'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
