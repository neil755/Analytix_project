from odoo import models, fields, api


class ProPaymentTerm(models.Model):
    _name = 'pro.payment'

    name = fields.Char(string='Payment Term')


class ProContactStatus(models.Model):
    _name = 'pro.contact.status'

    name = fields.Char(string='Contract Status')


class ProPackageType(models.Model):
    _name = 'pro.package.type'

    name = fields.Char(string='Package Type')


class ProPaymentStatus(models.Model):
    _name = 'pro.payment.status'

    name = fields.Char(string='Payment Status')


class ProjectProCustom(models.Model):
    _name = 'pro.custom'
    _description = 'PRO Contact List'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'client_code'

    serial_number = fields.Char(string="Sr. No.", readonly=True, copy=False)

    client_code = fields.Char(string='Client Code', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    project_id = fields.Many2one('project.project', string='Projects', domain="[('partner_id', '=', partner_id)]",
                                 tracking=True)
    contract_start = fields.Date(string='Contract Start Date', tracking=True)
    contract_end = fields.Date(string='Contract End Date', tracking=True)
    user_ids = fields.Many2many('res.users', string="Assigned To", tracking=True)
    contact_name = fields.Char(string='Contact Person', tracking=True)
    designation = fields.Char(string='Designation', tracking=True)
    phone_number = fields.Char(string='Phone Number', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    contract_amount = fields.Float(string='Contract Amount (SAR)', tracking=True)
    discount_amount = fields.Float(string='Discount Allowed', tracking=True)
    after_discount = fields.Float(string='After Discount', compute='_compute_after_discount', store=True, tracking=True)
    pro_payment = fields.Many2one('pro.payment', string='Payment Terms', tracking=True)
    payment_due = fields.Date(string='Next Payment Due', tracking=True)
    last_payment_amount = fields.Float(string='Last payment Amount', tracking=True)
    last_payment_date = fields.Date(string='Last payment Date', tracking=True)
    payment_remark = fields.Char(string='Last Payment Remark', tracking=True)
    pack_type = fields.Many2one('pro.package.type', string='Package Type', tracking=True)
    last_followup_date = fields.Date(string='Last Follow-up Date', tracking=True)
    next_followup_date = fields.Date(string='Next Follow-up Date', tracking=True)
    contact_status = fields.Many2one('pro.contact.status', string='Contract Status', tracking=True)
    payment_status = fields.Many2one('pro.payment.status', tracking=True)
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

    contact_attachment = fields.Many2many(
        'ir.attachment',
        'pro_custom_attachment_rel',
        'pro_custom_id',
        'attachment_id',
        string="DOC", tracking=True,
        help="Add relevant documents related to this file.",
        domain="[('res_model', '=', 'pro.custom'), ('res_id', '=', id)]")

    doc_attachment_ids = fields.Many2many(
        'ir.attachment', string="Attach File", compute='_compute_doc_attachment_ids',
        inverse='_inverse_doc_attachment_ids')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string="Attachments")

    @api.depends('attachment_ids')
    def _compute_doc_attachment_ids(self):
        for checklist in self:
            checklist.doc_attachment_ids = checklist.attachment_ids

    def _inverse_doc_attachment_ids(self):
        for checklist in self:
            checklist.attachment_ids = checklist.doc_attachment_ids

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

    @api.depends('contract_amount', 'discount_amount')
    def _compute_after_discount(self):
        for record in self:
            record.after_discount = record.contract_amount - record.discount_amount

    @api.model
    def create(self, vals):
        if not vals.get('serial_number'):
            vals['serial_number'] = self.env['ir.sequence'].next_by_code('pro.sequence.') or '/'
        return super(ProjectProCustom, self).create(vals)

    @api.onchange('project_id')
    def _onchange_pro_contract(self):
        self._compute_sale_line_id()

    def recompute_fields(self):
        """
        Method called by the button to recompute all dependent fields.
        """
        self._onchange_pro_contract()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
