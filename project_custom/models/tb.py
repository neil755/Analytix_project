from odoo import models, fields, api
import base64
import io
import xlsxwriter
from odoo.exceptions import UserError


class project_tb_custom(models.Model):
    _name = 'tb.custom'
    _description = 'TB with Adj'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'particulars'

    particulars = fields.Char(string='Particulars', tracking=True)
    op_balance = fields.Float(string='Opening Balance', tracking=True)
    dr_amount = fields.Float(string='DR Amount', tracking=True)
    cr_amount = fields.Float(string='CR Amount', tracking=True)
    close_balance = fields.Float(string='Closing Balance', compute='_compute_close_balance', store=True, tracking=True)
    adj_dr_amount = fields.Float(string='Adjustmemt Entries - DR Amount', tracking=True)
    adj_cr_amount = fields.Float(string='Adjustmemt Entries - CR Amount', tracking=True)
    final_balance = fields.Float(string='Final Balance', compute='_compute_final_balance', store=True, tracking=True)
    adj_remarks = fields.Char(string='Remarks', tracking=True)

    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    @api.depends('op_balance', 'dr_amount', 'cr_amount')
    def _compute_close_balance(self):
        for record in self:
            record.close_balance = record.op_balance + record.dr_amount - record.cr_amount

    @api.depends('close_balance', 'adj_dr_amount', 'adj_cr_amount')
    def _compute_final_balance(self):
        for record in self:
            record.final_balance = record.close_balance + record.adj_dr_amount - record.adj_cr_amount

    def action_tb_download_data(self):

        project_id = self.env.context.get('default_project_id', self.project_id.id if self.project_id else None)

        records = self.search([('project_id', '=', project_id)]) if project_id else self.search([])

        # Create an in-memory Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('TB with ADJ')

        # Add headers
        headers = ['ID', 'Project', 'Particulars', 'Opening Balance', 'DR Amount',
                   'CR Amount', 'Closing Balance', 'Adjustmemt Entries - DR Amount', 'Adjustmemt Entries - CR Amount',
                   'Final Balance', 'Remarks']
        for col, header in enumerate(headers):
            sheet.write(0, col, header)

            # Add data
        for row, record in enumerate(records, start=1):
            # Retrieve the external ID from ir.model.data
            external_id = ''
            record_model_data = self.env['ir.model.data'].search([
                ('model', '=', self._name),
                ('res_id', '=', record.id)
            ], limit=1)

            if record_model_data:
                external_id = f"{record_model_data.module}.{record_model_data.name}"
            else:
                # If no external ID exists, raise an error
                raise UserError(
                    f"No external ID found for record {record.id}. Please export it first to generate an external ID.")

            sheet.write(row, 0, external_id)
            sheet.write(row, 1, record.project_id.name or '')
            sheet.write(row, 2, record.particulars or '')
            sheet.write(row, 3, record.op_balance or '')
            sheet.write(row, 4, record.dr_amount or '')
            sheet.write(row, 5, record.cr_amount or '')
            sheet.write(row, 6, record.close_balance or '')
            sheet.write(row, 7, record.adj_dr_amount or '')
            sheet.write(row, 8, record.adj_cr_amount or '')
            sheet.write(row, 9, record.final_balance or '')
            sheet.write(row, 10, record.adj_remarks or '')

        workbook.close()
        output.seek(0)

        if not records:
            output.close()
            raise UserError("No records found to download.")

        attachment = self.env['ir.attachment'].create({
            'name': f'TB_with_ADJ_{project_id or "All"}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue()),
            'store_fname': f'TB_with_ADJ_{project_id or "All"}.xlsx',
            'res_model': 'tb.custom',
            'res_id': records[0].id,
        })

        output.close()

        # Return a download URL for the attachment
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


class ProjectTBCustom(models.Model):
    _inherit = 'project.project'

    def action_view_tb_custom(self):
        return {
            'name': 'TB with Adj ',
            'type': 'ir.actions.act_window',
            'res_model': 'tb.custom',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'default_company_id': self.company_id.id,
            },
        }
