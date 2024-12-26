from odoo import models, fields, api


class area_custom(models.Model):
    _name = 'area.custom'

    name = fields.Char(string="Area")


class status_custom(models.Model):
    _name = 'status.custom'

    name = fields.Char(string="Status")


class lead_status_project_custom(models.Model):
    _name = 'lead.status.project.custom'

    name = fields.Char(string="Status")


class project_custom(models.Model):
    _name = 'project.custom'
    _description = 'Requirement List'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sub_area'

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
        help="Add relevant files related to this Project."
    )

    @api.model
    def create(self, vals):
        if not vals.get('sequence_number'):
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code('sequence.serial') or '/'
        return super(project_custom, self).create(vals)


class ProjectRequirementList(models.Model):
    _inherit = 'project.project'

    lead_status = fields.Many2one('lead.status.project.custom', string='Lead Status', tracking=True)
    audit_lead = fields.Many2one('res.users', string="Audit Lead", tracking=True)

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
