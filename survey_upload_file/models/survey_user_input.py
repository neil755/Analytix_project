from odoo import api, fields, models
from odoo.exceptions import ValidationError
import base64
import binascii
import logging

_logger = logging.getLogger(__name__)


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    def _save_lines(self, question, answer, comment=None, overwrite_existing=False):
        if question.question_type == 'upload_file':
            old_answers = self.env['survey.user_input.line'].search([
                ('user_input_id', '=', self.id),
                ('question_id', '=', question.id),
            ])
            if answer and answer != [None, None]:  # Check for actual answer
                return self._save_line_file(question, old_answers, answer)
            elif old_answers:
                old_answers.unlink()  # Remove if no answer provided
            return self.env['survey.user_input.line']
        return super()._save_lines(question, answer, comment, overwrite_existing)

    def _save_line_file(self, question, old_answers, answer):
        vals = self._get_line_answer_file_upload_values(question, 'upload_file', answer)
        if old_answers:
            old_answers.write(vals)
            return old_answers
        return self.env['survey.user_input.line'].create(vals)

    def _get_line_answer_file_upload_values(self, question, answer_type, answer):
        vals = {
            'user_input_id': self.id,
            'question_id': question.id,
            'skipped': False,
            'answer_type': answer_type,
        }

        if answer_type == 'upload_file' and answer and isinstance(answer, list) and len(answer) >= 2:
            file_data = answer[0] if isinstance(answer[0], list) else [answer[0]]
            file_names = answer[1] if isinstance(answer[1], list) else [answer[1]]

            attachment_ids = []
            for data, name in zip(file_data, file_names):
                if data and name:  # Only process if we have both
                    try:
                        # Clean the base64 data
                        clean_data = data.split(',')[1] if ',' in data else data
                        # Validate base64
                        base64.b64decode(clean_data, validate=True)

                        attachment = self.env['ir.attachment'].sudo().create({
                            'name': name,
                            'type': 'binary',
                            'datas': clean_data,
                        })
                        attachment_ids.append(attachment.id)
                    except (ValueError, binascii.Error) as e:
                        _logger.error("Invalid base64 data for file upload: %s", str(e))
                        continue

            if attachment_ids:
                vals['value_file_data_ids'] = [(6, 0, attachment_ids)]

        return vals