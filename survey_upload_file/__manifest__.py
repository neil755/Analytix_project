# -*- coding: utf-8 -*-

{
    'name': "File Upload In Survey",
    'version': "17.0.1.0.1",
    'category': 'Extra Tools',
    'summary': 'Attachment of File in Survey Form',
    'description': 'This module is used for attachments of file in Survey Form,'
                   'You can also add multiple file attachment to Survey Form .',
    'author': 'Neil Antony Pinheiro',
    'company': 'Analytix',
    'depends': ['survey'],
    'assets': {
        'survey.survey_assets': [
            'survey_upload_file/static/src/js/survey_form_attachment.js',
            'survey_upload_file/static/src/js/SurveyFormWidget.js',
        ],
    },
    'data': [
        'views/survey_question_views.xml',
        'views/survey_user_views.xml',
        'views/survey_templates.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
