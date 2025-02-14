# -*- coding: utf-8 -*-

from odoo import models
import logging

_logger = logging.getLogger(__name__)


class SurveyUserInput(models.Model):
    """
    This class extends the 'survey.user_input' model to add custom
    functionality for saving user answers.

    Methods:
        _save_lines: Save the user's answer for the given question
        _save_line_file:Save the user's file upload answer for the given
        question
        _get_line_answer_file_upload_values:
        Get the values to use when creating or updating a user input line
        for a file upload answer
    """
    _inherit = "survey.user_input"

    def _save_lines(self, question, answer, comment=None,
                    overwrite_existing=False):
        """Save the user's answer for the given question."""
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id), ])
        if question.question_type in 'upload_file':
            res = self._save_line_simple_answer(question, old_answers, answer)
        else:
            res = super()._save_lines(question, answer, comment,
                                      overwrite_existing)
        return res

    def _save_line_simple_answer(self, question, old_answers, answer):
        """ Save the user's file upload answer for the given question."""
        vals = self._get_line_answer_file_upload_values(question,
                                                        'upload_file', answer)
        if old_answers:
            old_answers.write(vals)
            return old_answers
        else:
            return self.env['survey.user_input.line'].create(vals)

    def _get_line_answer_file_upload_values(self, question, answer_type, answer):
        vals = {
            'user_input_id': self.id,
            'question_id': question.id,
            'skipped': False,
            'answer_type': answer_type,
        }
        if answer_type == 'upload_file':
            if not isinstance(answer, list) or len(answer) < 2:
                _logger.error("Unexpected answer format: %s", answer)
                return vals  # Return empty values to avoid crashes

            file_data_list = answer[0]  # Should be a list of base64 file data
            file_name_list = answer[1]  # Should be a list of file names

            if not isinstance(file_data_list, list) or not isinstance(file_name_list, list):
                _logger.error("File data or names are not lists: %s, %s", file_data_list, file_name_list)
                return vals

            attachment_ids = []
            for index in range(len(file_name_list)):
                try:
                    file_name = file_name_list[index]
                    file_data = file_data_list[index]
                    if not file_name or not file_data:
                        _logger.warning("Skipping empty file or data: %s, %s", file_name, file_data)
                        continue

                    attachment = self.env['ir.attachment'].create({
                        'name': file_name,
                        'type': 'binary',
                        'datas': file_data,
                    })
                    attachment_ids.append(attachment.id)
                except Exception as e:
                    _logger.error("Error while creating attachment: %s", str(e))

            vals['value_file_data_ids'] = [(6, 0, attachment_ids)]
        return vals
