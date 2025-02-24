from odoo import models, fields, api
from datetime import date


class EscalationCustom(models.Model):
    _name = 'escalation.sheet'
    _description = 'Escalation Tracker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'


    name = fields.Char(string='Client Code', tracking=True)

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    created_date = fields.Date(string='Customer Requested Date', default=fields.Date.context_today, tracking=True)
    no_days = fields.Float(string='No. of Days', compute="_compute_no_days", store=True)

    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    project_id = fields.Many2one('project.project', string='Projects', domain="[('partner_id', '=', partner_id)]",
                                 tracking=True)
    milestone_id = fields.Many2one('project.milestone', string='Milestone', tracking=True,
                                   domain="[('project_id', '=', project_id), ('is_reached', '=', True)]")

    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string="Priority", tracking=True)
    pri_reason = fields.Char(string='Primary Reason', tracking=True)
    level1_remark = fields.Char(string='Remarks from L1', tracking=True)
    esc_user_id = fields.Many2one('res.users', string="Escalated By", tracking=True, default=lambda self: self.env.user)
    user_id = fields.Many2one('res.users', string="Escalated To", tracking=True)

    closed_date = fields.Date(string='Closed Date', tracking=True)
    remarks = fields.Html(string='Notes/Comments')

    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('hold', 'Hold'),
        ('resolved', 'Resolved'),
    ], default='new', tracking=True)

    reassign_level2 = fields.Many2one('res.users', string="Reassigned To L2", tracking=True)
    date_level2 = fields.Date(string='Reassign Date L2', tracking=True)
    no_days_level2 = fields.Float(string='No. of Days L2', compute="_compute_no_days_level2", store=True)
    level2_remark = fields.Char(string='Remarks from L2', tracking=True)
    show_reassign_fields_level2 = fields.Boolean(string="Is Reassigned to Level 2",
                                                 compute="_compute_show_reassign_fields_level2", store=True)

    # Level 3 Escalation
    reassign_level3 = fields.Many2one('res.users', string="Reassigned To L3", tracking=True)
    date_level3 = fields.Date(string='Reassign Date L3', tracking=True)
    no_days_level3 = fields.Float(string='No. of Days L3', compute="_compute_no_days_level3", store=True)
    level3_remark = fields.Char(string='Remarks from L3', tracking=True)
    show_reassign_fields_level3 = fields.Boolean(string="Is Reassigned to Level 3", store=True)

    # Level 4 Escalation
    reassign_level4 = fields.Many2one('res.users', string="Reassigned To L4", tracking=True)
    date_level4 = fields.Date(string='Reassign Date L4', tracking=True)
    no_days_level4 = fields.Float(string='No. of Days L4', compute="_compute_no_days_level4", store=True)
    level4_remark = fields.Char(string='Remarks from L4', tracking=True)
    show_reassign_fields_level4 = fields.Boolean(string="Is Reassigned to Level 4", store=True)

    # Level 5 Escalation
    reassign_level5 = fields.Many2one('res.users', string="Reassigned To L5", tracking=True)
    date_level5 = fields.Date(string='Reassign Date L5', tracking=True)
    no_days_level5 = fields.Float(string='No. of Days L5', compute="_compute_no_days_level5", store=True)
    level5_remark = fields.Char(string='Remarks from L5', tracking=True)
    show_reassign_fields_level5 = fields.Boolean(string="Is Reassigned to Level 5", store=True)

    @api.depends('created_date')
    def _compute_no_days(self):
        for record in self:
            if record.created_date:
                record.no_days = (date.today() - record.created_date).days
            else:
                record.no_days = 0

    @api.depends('date_level2')
    def _compute_no_days_level2(self):
        for record in self:
            if record.date_level2:
                record.no_days_level2 = (date.today() - record.date_level2).days
            else:
                record.no_days_level2 = 0

    @api.depends('date_level3')
    def _compute_no_days_level3(self):
        for record in self:
            record.no_days_level3 = (date.today() - record.date_level3).days if record.date_level3 else 0

    @api.depends('date_level4')
    def _compute_no_days_level4(self):
        for record in self:
            record.no_days_level4 = (date.today() - record.date_level4).days if record.date_level4 else 0

    @api.depends('date_level5')
    def _compute_no_days_level5(self):
        for record in self:
            record.no_days_level5 = (date.today() - record.date_level5).days if record.date_level5 else 0

    def action_hold(self):
        self.state = 'hold'

    def action_progress(self):
        self.state = 'in_progress'

    def action_resolve(self):
        self.write({
            'state': 'resolved',
            'closed_date': fields.Date.context_today(self),
        })

    def action_reassign_to_level2(self):
        """ Action to assign to Level 2 and update date """
        self.write({
            'show_reassign_fields_level2': True,
            'date_level2': fields.Date.context_today(self),
        })

    def action_reassign_to_level3(self):
        """ Action to assign to Level 3 and update date """
        self.write({
            'show_reassign_fields_level3': True,
            'date_level3': fields.Date.context_today(self),
        })

    def action_reassign_to_level4(self):
        """ Action to assign to Level 4 and update date """
        self.write({
            'show_reassign_fields_level4': True,
            'date_level4': fields.Date.context_today(self),
        })

    def action_reassign_to_level5(self):
        """ Action to assign to Level 5 and update date """
        self.write({
            'show_reassign_fields_level5': True,
            'date_level5': fields.Date.context_today(self),
        })

    # @api.model
    # def _cron_assign_to_team(self):
    #     """ Cron job to check escalations and send notifications when assigned. """
    #     today = date.today()
    #
    #     escalations = self.search([('state', '!=', 'resolved')])  # Get all unresolved records
    #     for record in escalations:
    #         assigned_user = None  # Initialize variable for the assigned user
    #
    #         if record.no_days >= 3 and not record.reassign_level2:
    #             record.write({'date_level2': today, 'show_reassign_fields_level2': True})
    #             assigned_user = record.reassign_level2
    #
    #         elif record.no_days_level2 >= 3 and not record.reassign_level3:
    #             record.write({'date_level3': today, 'show_reassign_fields_level3': True})
    #             assigned_user = record.reassign_level3
    #
    #         elif record.no_days_level3 >= 3 and not record.reassign_level4:
    #             record.write({'date_level4': today, 'show_reassign_fields_level4': True})
    #             assigned_user = record.reassign_level4
    #
    #         elif record.no_days_level4 >= 3 and not record.reassign_level5:
    #             record.write({'date_level5': today, 'show_reassign_fields_level5': True})
    #             assigned_user = record.reassign_level5
    #
    #         # If a user is assigned, send an email notification
    #         if assigned_user and assigned_user.partner_id.email:
    #             template = self.env.ref('project_custom.email_template_escalation_tracker')
    #             if template:
    #                 template.sudo().send_mail(record.id, force_send=True)
    #                 record.message_post(
    #                     body=f"Escalation assigned to {assigned_user.name}. Notification email sent.",
    #                     message_type="notification"
    #                 )
    #
    #     return True
