from odoo import models, fields, api
from datetime import datetime


class CreEnquiryStatus(models.Model):
    _name = 'cre.trackers.enquiry'

    name = fields.Char(string='Enquiry Type')


class CreTrackersStatus(models.Model):
    _name = 'cre.trackers.status'

    name = fields.Char(string='Resolution Status')


class CreFileTracker(models.Model):
    _name = 'cre.trackers'
    _description = 'CRE Tracker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'

    created_date = fields.Datetime(string='Customer Requested Date', default=lambda self: fields.Datetime.now(),
                                   tracking=True)
    start_date = fields.Datetime(string='Start Date', default=lambda self: fields.Datetime.now(),
                                   tracking=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        tracking=True
    )
    project_id = fields.Many2one('project.project', string='Projects', domain="[('partner_id', '=', partner_id)]",
                                 tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Priority', tracking=True)

    user_id = fields.Many2one('res.users', string="Assigned To", tracking=True)

    enquiry_type = fields.Many2one(
        'cre.trackers.enquiry', string='Enquiry Type', tracking=True
    )
    summary = fields.Char(string='Conversation Summary', tracking=True)
    response_date = fields.Datetime(string='Response given Date', default=lambda self: fields.Datetime.now(),
                                    tracking=True)
    response_time = fields.Char(
        string='Response Time',
        compute='_compute_response_time',
        store=True,
        tracking=True
    )
    esc_user_id = fields.Many2one('res.users', string="Escalated To", tracking=True)
    escalated_date = fields.Datetime(string='Escalated date', default=lambda self: fields.Datetime.now(),
                                     tracking=True)

    resolution_status = fields.Many2one(
        'cre.trackers.status', string='Resolution Status', tracking=True
    )

    resolved_days = fields.Integer(
        string='Resolved Days',
        compute='_compute_resolved_date',
        store=True,
        tracking=True
    )
    account_manager = fields.Many2one('res.users', related='project_id.account_manager', string="Account Manager",
                                      tracking=True)

    @api.depends('response_date', 'start_date')
    def _compute_response_time(self):
        for record in self:
            if record.response_date and record.start_date:
                delta = record.response_date - record.start_date
                total_seconds = delta.total_seconds()
                days = int(total_seconds // 86400)
                hours = int((total_seconds % 86400) // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                record.response_time = f"{days}d {hours}h {minutes}m {seconds}s"
            else:
                record.response_time = "0d 0h 0m 0s"

    @api.depends('resolution_status', 'created_date')
    def _compute_resolved_date(self):
        for record in self:
            if record.resolution_status and record.resolution_status.name.lower() == 'resolved' and record.created_date:
                delta = fields.Datetime.now() - record.created_date
                record.resolved_days = delta.days
            else:
                record.resolved_days = 0
