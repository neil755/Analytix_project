from odoo import models, fields, api
from datetime import datetime


class CreCategory(models.Model):
    _name = 'cre.categ'

    name = fields.Char(string='Follow up Category')


class CreResStatus(models.Model):
    _name = 'cre.resolution'

    name = fields.Char(string='Resolution Status')

class CreFileStatus(models.Model):
    _name = 'cre.file.status'

    name = fields.Char(string='File Status')


class ProjectCreCustom(models.Model):
    _name = 'cre.tracker'
    _description = 'Followup Tracker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Client Code', tracking=True)
    serial_number = fields.Char(string="Ticket", readonly=True, copy=False)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    created_date = fields.Date(string='Customer Requested Date', default=fields.Date.today, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    project_id = fields.Many2one('project.project', string='Projects', domain="[('partner_id', '=', partner_id)]",
                                 tracking=True)
    milestone_id = fields.Many2one('project.milestone', string='Milestone', tracking=True,
                                   domain="[('project_id', '=', project_id), ('is_reached', '=', True)]")

    followup = fields.Char(string='Followup Summary', tracking=True)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string="Priority", tracking=True)
    req_user_id = fields.Many2one('res.users', string="Requested by", tracking=True, default=lambda self: self.env.user)
    user_id = fields.Many2one('res.users', string="Assigned To", tracking=True)

    followup_categ = fields.Many2one('cre.categ', string='Follow up Category', tracking=True)
    resolution_status = fields.Many2one('cre.resolution', string='Resolution Status', tracking=True)
    file_status = fields.Many2one('cre.file.status', string='File Status', tracking=True)

    followup_date = fields.Date(string='Next Followup Date', tracking=True)
    remarks = fields.Html(string='Notes/Comments')

    @api.model
    def create(self, vals):
        if not vals.get('serial_number') or vals.get('serial_number') == '/':
            current_date = datetime.now()
            month_year = current_date.strftime('%m/%Y')
            sequence_number = self.env['ir.sequence'].next_by_code('cre_tracker.serial') or '0000'
            vals['serial_number'] = f"{month_year}/{sequence_number}"

        return super(ProjectCreCustom, self).create(vals)
