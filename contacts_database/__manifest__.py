# -*- coding: utf-8 -*-
{
    'name': "Contacts Database",

    'summary': "Contacts Database Management",

    'description': """
   Contacts Database Management """,

    'author': "Neil",
    'website': "https://github.com/neil755",

    'version': '1.0',

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
