# -*- coding: utf-8 -*-
{
    'name': "sale_taxinvoice_report",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Neil",
    'website': "https://github.com/neil755",

    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'sale_pdf_quote_builder', 'quotation_approval', 'sale_quotation_modification'],

    'data': [
        'report/ir_actions_report.xml',
        'views/templates.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',

}
