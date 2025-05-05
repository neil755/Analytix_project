from odoo import models, fields, api
import base64
import io
import xlsxwriter
from odoo.exceptions import UserError
import uuid


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
    project_id = fields.Many2one('project.project', string='Project', readonly=True, store=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'project_custom_attachment_rel',
        'project_custom_id',
        'attachment_id',
        string="DOC", tracking=True,
        help="Add relevant files related to this Project.(sequence.serial)",
        domain="[('res_model', '=', 'project.custom'), ('res_id', '=', id)]")




    product_id = fields.Many2one(
        'product.product',
        string='Service Requested',
        compute='_compute_product_id',
        store=True
    )
    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        tracking=True,
        compute='_compute_sale_line_id',
        store=True)
    salesperson_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        compute='_compute_salesperson_id',
        store=True,
        tracking=True
    )
    project_manager_id = fields.Many2one(
        'res.users',
        string='Project Manager',
        compute='_compute_project_manager_id',
        store=True,
        tracking=True
    )
    audit_lead_id = fields.Many2one(
        'res.users',
        string='Audit Lead',
        compute='_compute_audit_lead_id',
        store=True,
        tracking=True
    )
    lead_status_id = fields.Many2one('lead.status.project.custom', string='Project Status',
                                     compute='_compute_lead_status_id',
                                     store=True, tracking=True)
    tag_ids = fields.Many2many('project.tags', string='Audit Period',
                               compute='_compute_tag_ids',
                               store=True, tracking=True)

    doc_attachment_ids = fields.Many2many(
        'ir.attachment', string="Attach File", compute='_compute_doc_attachment_ids',
        inverse='_inverse_doc_attachment_ids')
    attachments_ids = fields.One2many('ir.attachment', 'res_id', string="Attachments")

    @api.depends('attachments_ids')
    def _compute_doc_attachment_ids(self):
        for checklist in self:
            checklist.doc_attachment_ids = checklist.attachments_ids

    def _inverse_doc_attachment_ids(self):
        for checklist in self:
            checklist.attachments_ids = checklist.doc_attachment_ids

    @api.depends('project_id')
    def _compute_project_manager_id(self):
        for record in self:
            record.project_manager_id = record.project_id.user_id if record.project_id else False

    @api.depends('project_id', 'project_id.sale_line_id')
    def _compute_sale_line_id(self):
        for record in self:
            if record.project_id and record.project_id.sale_line_id:
                record.sale_line_id = record.project_id.sale_line_id
            else:
                record.sale_line_id = False

    @api.depends('project_id')
    def _compute_audit_lead_id(self):
        for record in self:
            record.audit_lead_id = record.project_id.audit_lead if record.project_id else False

    @api.depends('project_id')
    def _compute_lead_status_id(self):
        for record in self:
            record.lead_status_id = record.project_id.lead_status if record.project_id else False

    @api.depends('sale_line_id')
    def _compute_salesperson_id(self):
        for record in self:
            record.salesperson_id = record.sale_line_id.order_id.user_id if record.sale_line_id and record.sale_line_id.order_id else False

    @api.depends('project_id')
    def _compute_tag_ids(self):
        for record in self:
            record.tag_ids = record.project_id.tag_ids if record.project_id else False

    @api.depends('sale_line_id', 'sale_line_id.product_id')
    def _compute_product_id(self):
        for record in self:
            if record.sale_line_id and record.sale_line_id.product_id:
                record.product_id = record.sale_line_id.product_id
            else:
                record.product_id = False

    @api.model
    def create(self, vals):
        if not vals.get('sequence_number'):
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code('sequence.serial') or '/'
        return super(project_custom, self).create(vals)

    def action_download_data(self):

        project_id = self.env.context.get('default_project_id', self.project_id.id if self.project_id else None)

        records = self.search([('project_id', '=', project_id)]) if project_id else self.search([])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Requirement List')

        # Add headers
        headers = ['ID', 'Sequence Number', 'Project', 'Area', 'Sub Area', 'Requirements',
                   'Reference', 'Request Date', 'Status Type', 'Receipt Date', 'Remarks']
        for col, header in enumerate(headers):
            sheet.write(0, col, header)

            # Add data
        for row, record in enumerate(records, start=1):
            # Retrieve the external ID from ir.model.data using sudo()
            external_id = ''
            record_model_data = self.env['ir.model.data'].sudo().search([
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
            sheet.write(row, 1, record.sequence_number or '')
            sheet.write(row, 2, record.project_id.name or '')
            sheet.write(row, 3, record.area.name or '')
            sheet.write(row, 4, record.sub_area or '')
            sheet.write(row, 5, record.req_list or '')
            sheet.write(row, 6, record.ref or '')
            sheet.write(row, 7, str(record.req_date) if record.req_date else '')
            sheet.write(row, 8, record.status_type.name or '')
            sheet.write(row, 9, str(record.receipt_date) if record.receipt_date else '')
            sheet.write(row, 10, record.remark or '')

        workbook.close()
        output.seek(0)

        if not records:
            output.close()
            raise UserError("No records found to download.")

        attachment = self.env['ir.attachment'].create({
            'name': f'Requirement_List_{project_id or "All"}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue()),
            'store_fname': f'Requirement_List_{project_id or "All"}.xlsx',
            'res_model': 'project.custom',
            'res_id': records[0].id,
        })

        output.close()

        # Return a download URL for the attachment
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


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
