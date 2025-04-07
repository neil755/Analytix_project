# -*- coding: utf-8 -*-
{
    'name': "project_custom",

    'summary': "In Project - Requirement List, TB and In Sales - CRE Tracker, PRO Contact List, Escalation Tracker",

    'description': """In Project - Requirement List, TB and In Sales - CRE Tracker, PRO Contact List, Escalation Tracker""",

    'author': "Neil",
    'website': "https://github.com/neil755",

    'version': '2.0',

    # any module necessary for this one to work correctly
    'depends': ['project', 'sale_project', 'utm', 'prodiz_project_customization', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/tb.xml',
        'views/pro.xml',
        'views/cre_tracker.xml',
        'views/escalation_sheet.xml',
    ],

    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
