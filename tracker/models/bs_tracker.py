from odoo import models, fields, api
from datetime import date


class BSTrackerClientCode(models.Model):
    _name = 'bs.tracker.client.code'

    name = fields.Char()


class BSTrackerStatus(models.Model):
    _name = 'bs.tracker.status'

    name = fields.Char()


class BSTrackerTransferStatus(models.Model):
    _name = 'bs.tracker.transfer.status'

    name = fields.Char()


class BSTrackerClearance(models.Model):
    _name = 'bs.tracker.clearance'

    name = fields.Char()


class BSTracker(models.Model):
    _name = 'bs.tracker'
    _description = 'BS Tracker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'

    code = fields.Many2one('bs.tracker.client.code', string='Code', tracking=True)
    client_code = fields.Char(
        string="Client Code",
        compute="_compute_client_code",
        inverse="_inverse_client_code",
        store=True,
        readonly=False  # Important for import
    )
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
    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        tracking=True,
        compute='_compute_sale_line_id',
        store=True)
    product_id = fields.Many2one(
        'product.product',
        string='Service Requested',
        compute='_compute_product_id',
        store=True
    )

    salesperson_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        compute='_compute_salesperson_id',
        store=True,
        tracking=True
    )
    sale_order_date = fields.Datetime(
        string='Sale Order Date',
        compute='_compute_sale_order_date',
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
    milestone_id = fields.Many2one('project.milestone', string='Milestone', tracking=True,
                                   domain="[('project_id', '=', project_id)]", compute='_compute_current_milestone',
                                   store=True)

    crm_tag_ids = fields.Many2many('crm.tag', string='CRM Tag',
                                   compute='_compute_crm_tag_ids',
                                   store=True, tracking=True)

    tag_ids = fields.Many2many('project.tags', string='Project Tag',
                               compute='_compute_tag_ids',
                               store=True, tracking=True)

    project_start_date = fields.Date(
        string='Project Start Date',
        compute='_compute_project_dates',
        store=True,
        tracking=True
    )
    project_end_date = fields.Date(
        string='Project End Date',
        compute='_compute_project_dates',
        store=True,
        tracking=True
    )
    current_stage_id = fields.Many2one(
        'project.project.stage',
        string='Current Stage',
        compute='_compute_current_stage',
        store=True,
        tracking=True
    )
    current_task_id = fields.Many2one(
        'project.task',
        string='Current Task',
        compute='_compute_current_task',
        store=True,
        tracking=True,
        domain="[('project_id', '=', project_id)]"
    )
    project_days = fields.Integer(
        string='Project Days',
        compute='_compute_project_days',
        store=True,
        help="Number of days since project started"
    )

    onboarding_status = fields.Many2one('bs.tracker.status', string='Onboarding Status', tracking=True)
    onboarding_start_date = fields.Date(string='Onboarding Start Date', tracking=True)
    onboarding_clearance = fields.Many2one('bs.tracker.clearance', string='Onboarding Payment Clearance',
                                           tracking=True)
    onboarding_meet_date = fields.Date(string='Onboarding Meeting Date', tracking=True)
    onboarding_complete_date = fields.Date(string='Onboarding Completed Date', tracking=True)
    onboarding_days = fields.Integer(
        string='Onboarding Days',
        compute='_compute_onboarding_days',
        store=True)
    onboarding_transfer = fields.Many2one('bs.tracker.transfer.status', string='Phase 1 Transfer Status',
                                          tracking=True)
    onboarding_remark = fields.Char(string='Onboarding Remarks', tracking=True)

    phase_one_status = fields.Many2one('bs.tracker.status', string='Phase 1 Status', tracking=True)
    phase_one_start_date = fields.Date(string='Phase 1 Start Date', tracking=True)
    misa_date = fields.Date(string='MISA Application Date', tracking=True)
    misa_approve_date = fields.Date(string='MISA Approved Date', tracking=True)
    phase_one_clearance = fields.Many2one('bs.tracker.clearance', string='Phase 1 Payment Clearance',
                                          tracking=True)
    phase_one_end_date = fields.Date(string='Phase 1 End Date', tracking=True)
    phase_one_days = fields.Integer(
        string='Phase 1 Days',
        compute='_compute_phase_one_days',
        store=True)
    phase_one_transfer = fields.Many2one('bs.tracker.transfer.status', string='Phase 2 Transfer Status',
                                         tracking=True)
    phase_one_remark = fields.Char(string='Phase 1 Remarks', tracking=True)

    phase_two_status = fields.Many2one('bs.tracker.status', string='Phase 2 Status', tracking=True)
    phase_two_start_date = fields.Date(string='Phase 2 Start Date', tracking=True)
    name_date = fields.Date(string='Name Approved Date', tracking=True)
    cr_date = fields.Date(string='CR Issued Date', tracking=True)
    phase_two_clearance = fields.Many2one('bs.tracker.clearance', string='Phase 2 Payment Clearance',
                                          tracking=True)
    phase_two_days = fields.Integer(
        string='Phase 2 Days',
        compute='_compute_phase_two_days',
        store=True)
    phase_two_transfer = fields.Many2one('bs.tracker.transfer.status', string='Phase 3 Transfer Status',
                                         tracking=True)
    phase_two_end_date = fields.Date(string='Phase 2 End Date', tracking=True)
    phase_two_remark = fields.Char(string='Phase 2 Remarks', tracking=True)

    phase_three_status = fields.Many2one('bs.tracker.status', string='Phase 3 Status', tracking=True)
    phase_three_start_date = fields.Date(string='Phase 3 Start Date', tracking=True)
    mol_date = fields.Date(string='MOL Issued Date', tracking=True)
    gm_date = fields.Date(string='GM VISA Issued Date', tracking=True)
    cr_linking_date = fields.Date(string='CR Linking Date', tracking=True)
    phase_three_clearance = fields.Many2one('bs.tracker.clearance', string='Phase 3 Payment Clearance',
                                            tracking=True)
    phase_three_days = fields.Integer(
        string='Phase 3 Days',
        compute='_compute_phase_three_days',
        store=True)
    phase_three_transfer = fields.Many2one('bs.tracker.transfer.status', string='Project Handover Status',
                                           tracking=True)
    phase_three_end_date = fields.Date(string='Phase 3 End Date', tracking=True)
    phase_three_remark = fields.Char(string='Phase 3 Remarks', tracking=True)

    handover_meet_date = fields.Date(string='Handover Meeting Date', tracking=True)
    doc_handover_date = fields.Date(string='Document Handover Date', tracking=True)
    fees = fields.Float(string='Fees', compute='_compute_fee_amount', store=True)

    @api.depends('code')
    def _compute_client_code(self):
        for record in self:
            if not record.client_code or not record.id:
                code_name = record.code.name if record.code else ''
                sequence = self.env['ir.sequence'].next_by_code('client.code.sequence') or '/'
                record.client_code = f"{code_name}-{sequence}" if code_name else sequence

    def _inverse_client_code(self):
        pass

    @api.model
    def create(self, vals):
        """Override create to ensure client_code is generated if not provided"""
        if 'client_code' not in vals or not vals.get('client_code'):
            code = self.env['bs.tracker.client.code'].browse(vals.get('code')).name if vals.get('code') else ''
            sequence = self.env['ir.sequence'].next_by_code('client.code.sequence') or '/'
            vals['client_code'] = f"{code}-{sequence}" if code else sequence
        return super(BSTracker, self).create(vals)

    @api.depends('phase_three_start_date', 'phase_three_end_date')
    def _compute_phase_three_days(self):
        for record in self:
            if record.phase_three_start_date and record.phase_three_end_date:
                delta = record.phase_three_end_date - record.phase_three_start_date
                record.phase_three_days = delta.days
            elif record.phase_three_start_date:
                today = date.today()
                delta = today - record.phase_three_start_date
                record.phase_three_days = delta.days
            else:
                record.phase_three_days = 0

    @api.depends('phase_two_start_date', 'phase_two_end_date')
    def _compute_phase_two_days(self):
        for record in self:
            if record.phase_two_start_date and record.phase_two_end_date:
                delta = record.phase_two_end_date - record.phase_two_start_date
                record.phase_two_days = delta.days
            elif record.phase_two_start_date:
                today = date.today()
                delta = today - record.phase_two_start_date
                record.phase_two_days = delta.days
            else:
                record.phase_two_days = 0

    @api.depends('phase_one_start_date', 'phase_one_end_date')
    def _compute_phase_one_days(self):
        for record in self:
            if record.phase_one_start_date and record.phase_one_end_date:
                delta = record.phase_one_end_date - record.phase_one_start_date
                record.phase_one_days = delta.days
            elif record.phase_one_start_date:
                today = date.today()
                delta = today - record.phase_one_start_date
                record.phase_one_days = delta.days
            else:
                record.phase_one_days = 0

    @api.depends('onboarding_start_date', 'onboarding_complete_date')
    def _compute_onboarding_days(self):
        for record in self:
            if record.onboarding_start_date and record.onboarding_complete_date:
                delta = record.onboarding_complete_date - record.onboarding_start_date
                record.onboarding_days = delta.days
            elif record.onboarding_start_date:
                today = date.today()
                delta = today - record.onboarding_start_date
                record.onboarding_days = delta.days
            else:
                record.onboarding_days = 0

    @api.depends('project_id', 'project_id.stage_id')
    def _compute_current_stage(self):
        for record in self:
            record.current_stage_id = record.project_id.stage_id if record.project_id else False

    @api.depends('project_start_date')
    def _compute_project_days(self):
        for record in self:
            if record.project_start_date:
                today = date.today()
                delta = today - record.project_start_date
                record.project_days = delta.days
            else:
                record.project_days = 0

    @api.depends('project_id', 'project_id.task_ids')
    def _compute_current_task(self):
        for record in self:
            if record.project_id and record.project_id.task_ids:
                record.current_task_id = record.project_id.task_ids.sorted('create_date', reverse=True)[0]
            else:
                record.current_task_id = False

    @api.depends('project_id')
    def _compute_current_milestone(self):
        for record in self:
            if record.project_id:
                # Get unreached milestones ordered by create_date (or id as fallback)
                milestone = self.env['project.milestone'].search([
                    ('project_id', '=', record.project_id.id),
                    ('is_reached', '=', False)
                ], order='create_date, id asc', limit=1)
                record.milestone_id = milestone if milestone else False
            else:
                record.milestone_id = False

    @api.depends('project_id')
    def _compute_project_dates(self):
        for record in self:
            if record.project_id:
                record.project_start_date = record.project_id.date_start
                record.project_end_date = record.project_id.date
            else:
                record.project_start_date = False
                record.project_end_date = False

    @api.depends('project_id', 'project_id.sale_line_id')
    def _compute_sale_line_id(self):
        for record in self:
            if record.project_id and record.project_id.sale_line_id:
                record.sale_line_id = record.project_id.sale_line_id
            else:
                record.sale_line_id = False

    @api.depends('project_id')
    def _compute_project_manager_id(self):
        for record in self:
            record.project_manager_id = record.project_id.user_id if record.project_id else False

    @api.depends('project_id')
    def _compute_audit_lead_id(self):
        for record in self:
            record.audit_lead_id = record.project_id.audit_lead if record.project_id else False

    @api.depends('sale_line_id')
    def _compute_sale_order_date(self):
        for record in self:
            record.sale_order_date = record.sale_line_id.order_id.date_order if record.sale_line_id and record.sale_line_id.order_id else False

    @api.depends('sale_line_id')
    def _compute_salesperson_id(self):
        for record in self:
            record.salesperson_id = record.sale_line_id.order_id.user_id if record.sale_line_id and record.sale_line_id.order_id else False

    @api.depends('partner_id', 'project_id')
    def _compute_crm_tag_ids(self):
        for record in self:
            crm_tags = False
            if record.partner_id:

                crm_leads = self.env['crm.lead'].search([
                    ('partner_id', '=', record.partner_id.id)
                ])
                if crm_leads:
                    crm_tags = crm_leads.mapped('tag_ids')
            record.crm_tag_ids = crm_tags

    @api.depends('project_id')
    def _compute_tag_ids(self):
        for record in self:
            record.tag_ids = record.project_id.tag_ids if record.project_id else False

    @api.depends('code')
    def _compute_client_code(self):
        for record in self:
            if record.code:
                code_name = record.code.name
                sequence = self.env['ir.sequence'].next_by_code('client.code.sequence') or '/'
                record.client_code = f"{code_name}-{sequence}"
            else:
                record.client_code = False

    @api.depends('sale_line_id', 'sale_line_id.price_subtotal')
    def _compute_fee_amount(self):
        for record in self:
            if record.sale_line_id:
                record.fees = record.sale_line_id.price_subtotal
            else:
                record.fees = 0

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self._compute_project_manager_id()
        self._compute_audit_lead_id()
        self._compute_tag_ids()
        self._compute_sale_line_id()
        self._compute_fee_amount()
        self._compute_current_stage()
        self._compute_current_task()
        self._compute_current_milestone()
        self._compute_project_dates()
        self._compute_crm_tag_ids()
        self._compute_salesperson_id()
        self._compute_sale_order_date()

    def write(self, vals):
        res = super(BSTracker, self).write(vals)
        if 'project_id' in vals:
            self._compute_project_manager_id()
            self._compute_audit_lead_id()
            self._compute_tag_ids()
            self._compute_sale_line_id()
            self._compute_fee_amount()
            self._compute_current_stage()
            self._compute_current_task()
            self._compute_current_milestone()
            self._compute_project_dates()
            self._compute_crm_tag_ids()
            self._compute_salesperson_id()
            self._compute_sale_order_date()
        return res

    def recompute_fields(self):
        """
        Method called by the button to recompute all dependent fields.
        """
        self._onchange_project_id()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
