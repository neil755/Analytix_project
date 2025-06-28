from odoo import models, fields, api


class EXTTrackerPaymentStatus(models.Model):
    _name = 'ext.tracker.payment.status'

    name = fields.Char(string='Payment Status')


class EXTTrackerWork(models.Model):
    _name = 'ext.tracker.work.status'

    name = fields.Char(string='Work Status')


class EXTTrackerDue(models.Model):
    _name = 'ext.tracker.due'

    name = fields.Char(string='Next Payment Due')


class EXTTrackerPayment(models.Model):
    _name = 'ext.tracker.payment'

    name = fields.Char(string='Payment Terms')


class EXTTrackerNature(models.Model):
    _name = 'ext.tracker.nature'

    name = fields.Char(string='Nature of Work')


class EXTTracker(models.Model):
    _name = 'ext.tracker'
    _description = 'EXT Tracker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'

    ext_number = fields.Char(string="Sr. No.", readonly=True, copy=False)

    client_code = fields.Char(string='Client Code', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    project_id = fields.Many2one('project.project', string='Projects', domain="[('partner_id', '=', partner_id)]",
                                 tracking=True)

    scope = fields.Char(string='Scope of work', tracking=True)

    user_ids = fields.Many2many('res.users', string="Assigned To", tracking=True)
    contact_name = fields.Char(string='Contact Person', tracking=True)
    phone_number = fields.Char(string='Phone Number', tracking=True)

    nature_work = fields.Many2many('ext.tracker.nature', string="Nature of work", tracking=True)

    amount = fields.Float(string='Amount', tracking=True)
    advance_amount = fields.Float(string='Advance Amount', tracking=True)
    payment = fields.Many2one('ext.tracker.payment', string='Payment Terms', tracking=True)
    payment_due = fields.Many2one('ext.tracker.due', string='Next Payment Due', tracking=True)
    payment_status = fields.Many2one('ext.tracker.payment.status', string='Payment Status', tracking=True)
    payment_remark = fields.Char(string='Last Payment Remark', tracking=True)

    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)

    # last_followup_date = fields.Date(string='Last Follow-up Date', tracking=True)
    next_followup_date = fields.Date(string='Next Follow-up Date', tracking=True)
    work_status = fields.Many2one('ext.tracker.work.status', string='Work Status', tracking=True)

    remark = fields.Html(string='Remarks')
    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        tracking=True,
        compute='_compute_sale_line_id',
        store=True)

    sale_order_date = fields.Datetime(
        string='Sale Order Date',
        compute='_compute_sale_order_date',
        store=True,
        tracking=True
    )
    salesperson_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        compute='_compute_salesperson_id',
        store=True,
        tracking=True

    )

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    @api.depends('project_id', 'project_id.sale_line_id')
    def _compute_sale_line_id(self):
        for record in self:
            if record.project_id and record.project_id.sale_line_id:
                record.sale_line_id = record.project_id.sale_line_id
            else:
                record.sale_line_id = False

    @api.depends('sale_line_id')
    def _compute_sale_order_date(self):
        for record in self:
            record.sale_order_date = record.sale_line_id.order_id.date_order if record.sale_line_id and record.sale_line_id.order_id else False

    @api.depends('sale_line_id')
    def _compute_salesperson_id(self):
        for record in self:
            record.salesperson_id = record.sale_line_id.order_id.user_id if record.sale_line_id and record.sale_line_id.order_id else False

    @api.model
    def create(self, vals):
        if not vals.get('ext_number'):
            vals['ext_number'] = self.env['ir.sequence'].next_by_code('ext.sequence.') or '/'
        return super(EXTTracker, self).create(vals)

    @api.onchange('project_id')
    def _onchange_ext_tracker(self):
        self._compute_sale_line_id()
        self._compute_sale_order_date()
        self._compute_salesperson_id()

    def recompute_fields(self):
        """
        Method called by the button to recompute all dependent fields.
        """
        self._onchange_ext_tracker()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
