# -*- coding: utf-8 -*-

from odoo import fields, models


class SurveyQuestion(models.Model):
    """
    This class extends the 'survey.question' model to add new functionality
    for file uploads.
    """
    _inherit = 'survey.question'

    question_type = fields.Selection(
        selection_add=[('upload_file', 'Upload File')],
        help='Select the type of question to create.')
    upload_multiple_file = fields.Boolean(string='Upload Multiple File',
                                          help='Check this box if you want to '
                                               'allow users to upload '
                                               'multiple files')
