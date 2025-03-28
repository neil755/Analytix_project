# -*- coding: utf-8 -*-
{
    'name': "crm_welcome_mail",

    'summary': 'CRM Welcome Mail',

    'description': """
Send welcome email to customers when a lead is created
    """,

    'author': "Neil Antony Pinheiro",

    'category': 'CRM',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',

    ],
    'installable': True,
    'application': True,
}
