from odoo import models, fields, api
import base64
import io
import xlsxwriter


class area_custom(models.Model):
    _name = 'area.custom'

    name = fields.Char(string="Area")


class status_custom(models.Model):
    _name = 'status.custom'

    name = fields.Char(string="Status")


class lead_status_project_custom(models.Model):
    _name = 'lead.status.project.custom'

    name = fields.Char(string="Status")


class lead_test_project_custom(models.Model):
    _name = 'lead.test.project.custom'

    name = fields.Char(string="Test")


class project_custom(models.Model):
    _name = 'project.custom'
    _description = 'Requirement List'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sub_area'

    name = fields.Char()
    area = fields.Many2one('area.custom', string='Area', tracking=True)

    sub_area = fields.Char(string="Sub Area", tracking=True)
    status_type = fields.Many2one('status.custom', string='Status', tracking=True)
    req_list = fields.Char(string='Particulars/Requirements in Details', tracking=True)
    ref = fields.Char(string="Reference", tracking=True)

    req_date = fields.Date(string='Request of Date', tracking=True)
    receipt_date = fields.Date(string='Receipt of Date', tracking=True)

    remark = fields.Char(string="Remarks", tracking=True)
    sequence_number = fields.Char(string="Serial Number", readonly=True, copy=False)
    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Attachments", tracking=True,
        help="Add relevant files related to this Project.(sequence.serial)"
    )

    @api.model
    def create(self, vals):
        if not vals.get('sequence_number'):
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code('sequence.serial') or '/'
        return super(project_custom, self).create(vals)

    # def action_download_data(self):
    #     # Check if the action is triggered for a specific project
    #     project_id = self.env.context.get('default_project_id')
    #
    #     # Fetch records for the specific project, if provided
    #     records = self.search([('project_id', '=', project_id)]) if project_id else self.search([])
    #
    #     # Create an in-memory Excel file
    #     output = io.BytesIO()
    #     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    #     sheet = workbook.add_worksheet('Requirement List')
    #
    #     # Add headers
    #     headers = ['Sequence Number', 'External ID', 'Project', 'Area', 'Sub Area', 'Requirements',
    #                'Reference', 'Request Date', 'Status Type', 'Receipt Date', 'Remarks']
    #     for col, header in enumerate(headers):
    #         sheet.write(0, col, header)
    #
    #         # Add data
    #     for row, record in enumerate(records, start=1):
    #         external_id = ''
    #         model_data = self.env['ir.model.data'].search(
    #             [('model', '=', 'project.custom'), ('res_id', '=', record.id)],
    #             limit=1
    #         )
    #         if model_data:
    #             external_id = f"{model_data.module}.{model_data.name}"
    #
    #         sheet.write(row, 0, record.sequence_number or '')
    #         sheet.write(row, 1, external_id)
    #         sheet.write(row, 2, record.project_id.name or '')
    #         sheet.write(row, 3, record.area.name or '')
    #         sheet.write(row, 4, record.sub_area or '')
    #         sheet.write(row, 5, record.req_list or '')
    #         sheet.write(row, 6, record.ref or '')
    #         sheet.write(row, 7, str(record.req_date) if record.req_date else '')
    #         sheet.write(row, 8, record.status_type.name or '')
    #         sheet.write(row, 9, str(record.receipt_date) if record.receipt_date else '')
    #         sheet.write(row, 10, record.remark or '')
    #
    #     workbook.close()
    #     output.seek(0)
    #
    #     # Create an attachment and return as a downloadable file
    #     attachment = self.env['ir.attachment'].create({
    #         'name': f'Requirement_List_{project_id or "All"}.xlsx',
    #         'type': 'binary',
    #         'datas': base64.b64encode(output.getvalue()),
    #         'store_fname': f'Requirement_List_{project_id or "All"}.xlsx',
    #         'res_model': self._name,
    #         'res_id': self.id,
    #     })
    #
    #     output.close()
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': f'/web/content/{attachment.id}?download=true',
    #         'target': 'self',
    #     }


class ProjectRequirementList(models.Model):
    _inherit = 'project.project'

    product_id = fields.Many2one('product.product', 'Service Requested', related="sale_line_id.product_id", store=True)
    lead_status = fields.Many2one('lead.status.project.custom', string='Project Status', tracking=True)
    audit_lead = fields.Many2one('res.users', string="Project Lead", tracking=True)

    def action_view_requirement_list(self):
        """Button action to view or create linked requirement lists dynamically."""
        return {
            'name': 'Requirement List',
            'type': 'ir.actions.act_window',
            'res_model': 'project.custom',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'default_company_id': self.company_id.id,
            },
        }

    def write(self, vals):
        """Override the write method to update tasks when audit_lead is changed."""
        res = super(ProjectRequirementList, self).write(vals)  # Call the parent write method
        if 'audit_lead' in vals:
            for project in self:
                # Include both active and archived tasks
                tasks = self.env['project.task'].with_context(active_test=False).search(
                    [('project_id', '=', project.id)])
                for task in tasks:
                    if vals['audit_lead'] not in task.user_ids.ids:
                        task.user_ids = [(4, vals['audit_lead'])]  # Add the new audit_lead to the task's user_ids
        return res


class ProjectTask(models.Model):
    _inherit = 'project.task'

    audit_lead = fields.Many2one('res.users', string="Audit Lead", related='project_id.audit_lead', store=True)
