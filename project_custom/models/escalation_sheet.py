import logging
from odoo import models, fields, api
from datetime import date

_logger = logging.getLogger(__name__)


class PrimaryReason(models.Model):
    _name = 'escalation.primary.reason'

    name = fields.Char(string='Primary Reason')


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
    no_days = fields.Float(string='No. of Days', compute="_compute_no_days", store=False)

    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    project_id = fields.Many2one('project.project', string='Projects', domain="[('partner_id', '=', partner_id)]",
                                 tracking=True)
    milestone_id = fields.Many2one('project.milestone', string='Milestone', tracking=True,
                                   domain="[('project_id', '=', project_id)]")


    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string="Priority", tracking=True)
    pri_reason = fields.Char(string='Primary Reason', tracking=True)
    primary_reason = fields.Many2one('escalation.primary.reason', string='Primary Reason', tracking=True)
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
    level_status = fields.Selection([
        ('1', 'Level 1'),
        ('2', 'Level 2'),
        ('3', 'Level 3'),
        ('4', 'Level 4'),
        ('5', 'Level 5'),
    ], default='1', tracking=True)

    reassign_level2 = fields.Many2one('res.users', string="Reassigned To L2", tracking=True)
    date_level2 = fields.Date(string='Reassign Date L2', tracking=True)
    no_days_level2 = fields.Float(string='No. of Days L2', compute="_compute_no_days_level2", store=False)
    level2_remark = fields.Char(string='Remarks from L2', tracking=True)
    show_reassign_fields_level2 = fields.Boolean(string="Is Reassigned to Level 2",
                                                 compute="_compute_show_reassign_fields_level2", store=True)

    # Level 3 Escalation
    reassign_level3 = fields.Many2one('res.users', string="Reassigned To L3", tracking=True)
    date_level3 = fields.Date(string='Reassign Date L3', tracking=True)
    no_days_level3 = fields.Float(string='No. of Days L3', compute="_compute_no_days_level3", store=False)
    level3_remark = fields.Char(string='Remarks from L3', tracking=True)
    show_reassign_fields_level3 = fields.Boolean(string="Is Reassigned to Level 3", store=True)

    # Level 4 Escalation
    reassign_level4 = fields.Many2one('res.users', string="Reassigned To L4", tracking=True)
    date_level4 = fields.Date(string='Reassign Date L4', tracking=True)
    no_days_level4 = fields.Float(string='No. of Days L4', compute="_compute_no_days_level4", store=False)
    level4_remark = fields.Char(string='Remarks from L4', tracking=True)
    show_reassign_fields_level4 = fields.Boolean(string="Is Reassigned to Level 4", store=True)

    # Level 5 Escalation
    reassign_level5 = fields.Many2one('res.users', string="Reassigned To L5", tracking=True)
    date_level5 = fields.Date(string='Reassign Date L5', tracking=True)
    no_days_level5 = fields.Float(string='No. of Days L5', compute="_compute_no_days_level5", store=False)
    level5_remark = fields.Char(string='Remarks from L5', tracking=True)
    show_reassign_fields_level5 = fields.Boolean(string="Is Reassigned to Level 5", store=True)

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Attachments", tracking=True,
        help="Add relevant files related to this Project"
    )

    @api.depends('created_date')
    def _compute_no_days(self):
        today = date.today()
        for record in self:
            if record.created_date:
                record.no_days = (today - record.created_date).days
            else:
                record.no_days = 0

    @api.depends('date_level2')
    def _compute_no_days_level2(self):
        today = date.today()
        for record in self:
            if record.date_level2:
                record.no_days_level2 = (today - record.date_level2).days
            else:
                record.no_days_level2 = 0

    @api.depends('date_level3')
    def _compute_no_days_level3(self):
        today = date.today()
        for record in self:
            record.no_days_level3 = (today - record.date_level3).days if record.date_level3 else 0

    @api.depends('date_level4')
    def _compute_no_days_level4(self):
        today = date.today()
        for record in self:
            record.no_days_level4 = (today - record.date_level4).days if record.date_level4 else 0

    @api.depends('date_level5')
    def _compute_no_days_level5(self):
        today = date.today()
        for record in self:
            record.no_days_level5 = (today - record.date_level5).days if record.date_level5 else 0

    def action_hold(self):
        self.state = 'hold'

    def action_progress(self):
        self.state = 'in_progress'

    def action_resolve(self):
        self.write({
            'state': 'resolved',
            'closed_date': fields.Date.context_today(self),
        })

    def _notify_user(self, user, message):
        """ Helper method to notify user via email """
        _logger.info(f"Notifying user {user.name} ({user.email}) with message: {message}")
        if not user.email:
            _logger.error(f"User {user.name} does not have a valid email address.")
            return
        self.message_post(
            partner_ids=user.partner_id.ids,
            body=message,
            subject="Escalation Assignment Notification",
            message_type="comment",
            subtype_id=self.env.ref('mail.mt_comment').id,
        )
        _logger.info("Notification sent successfully.")

    @api.model
    def create(self, vals):
        """ Override create method to notify user when record is created """
        record = super(EscalationCustom, self).create(vals)
        if record.user_id:
            message = f"You have been assigned to the Escalation Tracker : {record.partner_id.name}."
            record._notify_user(record.user_id, message)
        return record

    def write(self, vals):
        """ Override write method to notify user when assigned to any level """
        if 'user_id' in vals and vals['user_id']:
            user = self.env['res.users'].browse(vals['user_id'])
            message = f"You have been assigned to the Escalation Tracker : {self.partner_id.name}."
            self._notify_user(user, message)

        if 'reassign_level2' in vals and vals['reassign_level2']:
            user = self.env['res.users'].browse(vals['reassign_level2'])
            message = f"You have been reassigned for the Escalation Tracker(L2) : {self.partner_id.name}."
            self._notify_user(user, message)

        if 'reassign_level3' in vals and vals['reassign_level3']:
            user = self.env['res.users'].browse(vals['reassign_level3'])
            message = f"You have been reassigned for the Escalation Tracker(L3) : {self.partner_id.name}."
            self._notify_user(user, message)

        if 'reassign_level4' in vals and vals['reassign_level4']:
            user = self.env['res.users'].browse(vals['reassign_level4'])
            message = f"You have been reassigned for the Escalation Tracker(L4) : {self.partner_id.name}."
            self._notify_user(user, message)

        if 'reassign_level5' in vals and vals['reassign_level5']:
            user = self.env['res.users'].browse(vals['reassign_level5'])
            message = f"You have been reassigned for the Escalation Tracker(L5) : {self.partner_id.name}."
            self._notify_user(user, message)

        return super(EscalationCustom, self).write(vals)

    def action_reassign_to_level2(self):
        """ Action to assign to Level 2 and update date """
        self.write({
            'show_reassign_fields_level2': True,
            'date_level2': fields.Date.context_today(self),
            'level_status': '2',
        })

    def action_reassign_to_level3(self):
        """ Action to assign to Level 3 and update date """
        self.write({
            'show_reassign_fields_level3': True,
            'date_level3': fields.Date.context_today(self),
            'level_status': '3',
        })

    def action_reassign_to_level4(self):
        """ Action to assign to Level 4 and update date """
        self.write({
            'show_reassign_fields_level4': True,
            'date_level4': fields.Date.context_today(self),
            'level_status': '4',
        })

    def action_reassign_to_level5(self):
        """ Action to assign to Level 5 and update date """
        self.write({
            'show_reassign_fields_level5': True,
            'date_level5': fields.Date.context_today(self),
            'level_status': '5',
        })
