from odoo import models, fields, api


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    def _save_lines(self, question, answer, comment=None, overwrite_existing=False):
        """Save the user's answer for the given question."""
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id),
        ])
        if question.question_type == 'upload_file':
            res = self._save_line_simple_answer(question, old_answers, answer)
        else:
            res = super()._save_lines(question, answer, comment, overwrite_existing)
        return res

    def _save_line_simple_answer(self, question, old_answers, answer):
        """Save the user's file upload answer for the given question."""
        vals = self._get_line_answer_file_upload_values(question, 'upload_file', answer)
        if old_answers:
            old_answers.write(vals)
            return old_answers
        else:
            return self.env['survey.user_input.line'].create(vals)

    def _get_line_answer_file_upload_values(self, question, answer_type, answer):
        """Get the values to use when creating or updating a user input line for a file upload answer."""
        vals = {
            'user_input_id': self.id,
            'question_id': question.id,
            'skipped': False,
            'answer_type': answer_type,
        }
        if answer_type == 'upload_file':
            attachment_ids = []
            if answer and len(answer) >= 2:
                file_data = answer[0]
                file_name = answer[1]
                if isinstance(file_data, list) and isinstance(file_name, list):
                    for data, name in zip(file_data, file_name):
                        if data and name:
                            attachment = self.env['ir.attachment'].create({
                                'name': name,
                                'type': 'binary',
                                'datas': data,
                                'mimetype': 'application/octet-stream',  # Set a default mimetype
                            })
                            attachment_ids.append(attachment.id)
            vals['value_file_data_ids'] = [(6, 0, attachment_ids)]
        return vals
