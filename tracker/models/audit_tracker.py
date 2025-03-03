from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class AuditPaymentStatus(models.Model):
    _name = 'audit.payment.status'

    name = fields.Char()


class AuditReviewStatus(models.Model):
    _name = 'audit.review.status'

    name = fields.Char()


class AuditTracker(models.Model):
    _name = 'audit.tracker'
    _description = 'Audit Tracker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'client_code'

    client_code = fields.Char(string='Client Code', tracking=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        compute='_compute_partner_id',
        store=True,
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
    lead_status_id = fields.Many2one('lead.status.project.custom', string='Project Status',
                                     compute='_compute_lead_status_id',
                                     store=True, tracking=True)

    engagement_sign_date = fields.Date(string='Engagement Signing Date', tracking=True)
    payment_followup_assign_id = fields.Many2one('res.users', string='Payment Followup Assigned To', tracking=True)
    fees = fields.Float(string='Fees', compute='_compute_fee_amount', store=True)
    first_payment = fields.Float(string='First Payment Amount')
    first_payment_status = fields.Many2one('audit.payment.status', tracking=True)
    first_payment_received_date = fields.Date(string='First Payment Received Date', tracking=True)
    second_payment = fields.Float(string='Second Payment Amount')
    second_payment_status = fields.Many2one('audit.payment.status', tracking=True)
    second_payment_received_date = fields.Date(string='Second Payment Received Date', tracking=True)
    final_payment = fields.Float(string='Final Payment Amount')
    final_payment_status = fields.Many2one('audit.payment.status', tracking=True)
    final_payment_received_date = fields.Date(string='Final Payment Received Date', tracking=True)

    assigned_to_id = fields.Many2one('res.users', string='Assigned To', tracking=True)
    audit_status = fields.Many2one('audit.review.status', string='Audit Requirements Status', tracking=True)
    audit_req_sharing_date = fields.Date(string='Audit Requirements Sharing Date', tracking=True)
    audit_req_receiving_date = fields.Date(string='Audit Requirements Receiving Date', tracking=True)
    received_documents = fields.Integer(string='Received Documents', compute='_compute_received_documents', store=True)
    pending_documents = fields.Integer(string='Pending Documents', compute='_compute_pending_documents', store=True)

    assigned_to_audit_id = fields.Many2one('res.users', string='Audit Requirements Assigned To', tracking=True)
    tb_status = fields.Many2one('audit.review.status', string='TB/Audit Queries Status', tracking=True)
    last_audit_sharing_date = fields.Date(string='Last Audit Queries Sharing Date', tracking=True)
    last_audit_receiving_date = fields.Date(string='last Audit Queries Receiving Date from Client', tracking=True)
    audit_remark = fields.Char(string='Remarks', tracking=True)

    initial_review_date = fields.Date(string='Date of Sharing for Initial Review', tracking=True)
    initial_status = fields.Many2one('audit.review.status', string='Analytix First Review Status', tracking=True)
    assigned_to_initial_id = fields.Many2one('res.users', string='Initial Review Assigned To', tracking=True)
    initial_complete_date = fields.Date(string='Date of Sharing for Initial Review', tracking=True)
    initial_remark = fields.Char(string='Remarks for Initial Review', tracking=True)

    abcpa_review_date = fields.Date(string='Date of Sharing for ABCPA Review', tracking=True)
    abcpa_status = fields.Many2one('audit.review.status', string='ABCPA First Review Status', tracking=True)
    assigned_to_abcpa_id = fields.Many2one('res.users', string='ABCPA Review Assigned To', tracking=True)
    abcpa_complete_date = fields.Date(string='Date of Receiving the File from ABCPA', tracking=True)
    abcpa_remark = fields.Char(string='Remarks for ABCPA Review', tracking=True)

    second_status = fields.Many2one('audit.review.status', string='Analytix Second Review Status', tracking=True)
    second_analytix_date = fields.Date(string='Date of sharing for Second review',
                                       tracking=True)
    assigned_to_second_id = fields.Many2one('res.users', string='Second Review Assigned To', tracking=True)
    second_review_date = fields.Date(string='Date of Sharing Final Requirements with Client after Audit Review',
                                     tracking=True)
    second_review_receive_date = fields.Date(string='Date of Receiving Final Requirements from Client', tracking=True)
    second_remark = fields.Char(string='Remarks for Final Review', tracking=True)

    manager_status = fields.Many2one('audit.review.status', string='Analytix Manager Status', tracking=True)
    manager_analytix_date = fields.Date(string='Date of sharing for Manager review ',
                                        tracking=True)
    assigned_to_manager_id = fields.Many2one('res.users', string='Manager Assigned To', tracking=True)
    manager_remark = fields.Char(string='Manager Remarks', tracking=True)

    abcpa_final_status = fields.Many2one('audit.review.status', string='ABCPA Final Review Status', tracking=True)
    assigned_to_abcpa_final_id = fields.Many2one('res.users', string='ABCPA Review Assigned To', tracking=True)
    abcpa_final_share_date = fields.Date(string='Last Date of sharing Audit file to ABCPA', tracking=True)
    abcpa_final_receive_date = fields.Date(string='Final Date of receiving queries from ABCPA', tracking=True)
    abcpa_final_reply_date = fields.Date(string='Date of replying queries to ABCPA', tracking=True)
    abcpa_final_remark = fields.Char(string='ABCPA Final Review Remarks', tracking=True)

    final_review_date = fields.Date(string='Date of receiving draft report', tracking=True)
    final_status = fields.Many2one('audit.review.status', string='Final Audit Status', tracking=True)
    assigned_to_final_id = fields.Many2one('res.users', string='Final Audit Assigned To', tracking=True)
    final_share_date = fields.Date(string='Date of sharing draft to client', tracking=True)
    final_receive_date = fields.Date(string='Date of receiving signed draft from client', tracking=True)
    final_report_date = fields.Date(string='Date of Audit Report uploading', tracking=True)
    final_remark = fields.Char(string='Final Audit Remarks', tracking=True)

    zakat_status = fields.Many2one('audit.review.status', string='ZAKAT Status', tracking=True)
    assigned_to_zakat_id = fields.Many2one('res.users', string='ZAKAT Assigned To', tracking=True)
    zakat_complete_date = fields.Date(string='Date of giving for ZAKAT Filing', tracking=True)
    zakat_file_date = fields.Date(string='Date of ZAKAT Filing', tracking=True)
    zakat_remark = fields.Char(string='ZAKAT Remarks', tracking=True)

    @api.depends('project_id')
    def _compute_received_documents(self):
        for record in self:
            if record.project_id:

                record.received_documents = self.env['project.custom'].search_count([
                    ('project_id', '=', record.project_id.id),
                    ('status_type', '=', 'Received')
                ])
            else:
                record.received_documents = 0

    @api.depends('project_id')
    def _compute_pending_documents(self):
        for record in self:
            if record.project_id:

                record.pending_documents = self.env['project.custom'].search_count([
                    ('project_id', '=', record.project_id.id),
                    ('status_type', '=', 'Pending')
                ])
            else:
                record.pending_documents = 0

    @api.depends('project_id', 'project_id.sale_line_id')
    def _compute_sale_line_id(self):
        for record in self:
            _logger.info(f"Computing sale_line_id for record {record.id}")
            if record.project_id and record.project_id.sale_line_id:
                record.sale_line_id = record.project_id.sale_line_id
                _logger.info(f"sale_line_id set to {record.project_id.sale_line_id.id}")
            else:
                record.sale_line_id = False
                _logger.info("sale_line_id set to False")

    def _compute_partner_id(self):
        for record in self:
            if record.project_id and record.project_id.partner_id:
                record.partner_id = record.project_id.partner_id
            else:
                record.partner_id = False

    def _compute_project_manager_id(self):
        for record in self:
            if record.project_id and record.project_id.user_id:
                record.project_manager_id = record.project_id.user_id
            else:
                record.project_manager_id = False

    def _compute_audit_lead_id(self):
        for record in self:
            if record.project_id and record.project_id.audit_lead:
                record.audit_lead_id = record.project_id.audit_lead
            else:
                record.audit_lead_id = False

    def _compute_lead_status_id(self):
        for record in self:
            if record.project_id and record.project_id.lead_status:
                record.lead_status_id = record.project_id.lead_status
            else:
                record.lead_status_id = False

    @api.depends('sale_line_id', 'sale_line_id.product_id')
    def _compute_product_id(self):
        for record in self:
            _logger.info(f"Computing product_id for record {record.id}")
            if record.sale_line_id and record.sale_line_id.product_id:
                record.product_id = record.sale_line_id.product_id
                _logger.info(f"product_id set to {record.sale_line_id.product_id.id}")
            else:
                record.product_id = False
                _logger.info("product_id set to False")

    def _compute_sale_order_date(self):
        for record in self:
            if record.sale_line_id and record.sale_line_id.order_id:
                record.sale_order_date = record.sale_line_id.order_id.date_order
            else:
                record.sale_order_date = False

    def _compute_salesperson_id(self):
        for record in self:
            if record.sale_line_id and record.sale_line_id.order_id.user_id:
                record.salesperson_id = record.sale_line_id.order_id.user_id
            else:
                record.salesperson_id = False

    @api.depends('sale_line_id', 'sale_line_id.price_subtotal')
    def _compute_fee_amount(self):
        for record in self:
            _logger.info(f"Computing fees for record {record.id}")
            if record.sale_line_id:
                record.fees = record.sale_line_id.price_subtotal
                _logger.info(f"fees set to {record.sale_line_id.price_subtotal}")
            else:
                record.fees = 0
                _logger.info("fees set to 0")

    @api.onchange('project_id')
    def _onchange_project_id(self):
        """
        Automatically populate fields when project_id is selected.
        """
        if self.project_id:
            self.partner_id = self.project_id.partner_id
            self.sale_line_id = self.project_id.sale_line_id
            self.product_id = self.project_id.sale_line_id.product_id if self.project_id.sale_line_id else False
            self.salesperson_id = self.project_id.sale_line_id.order_id.user_id if self.project_id.sale_line_id and self.project_id.sale_line_id.order_id else False
            self.sale_order_date = self.project_id.sale_line_id.order_id.date_order if self.project_id.sale_line_id and self.project_id.sale_line_id.order_id else False
            self.project_manager_id = self.project_id.user_id
            self.audit_lead_id = self.project_id.audit_lead
            self.lead_status_id = self.project_id.lead_status


class ProjectAuditTracker(models.Model):
    _inherit = 'project.project'

    def action_view_audit_tracker(self):
        return {
            'name': 'Audit Tracker',
            'type': 'ir.actions.act_window',
            'res_model': 'audit.tracker',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'default_partner_id': self.partner_id.id if self.partner_id else False,
                'default_company_id': self.company_id.id,
                'default_product_id': self.sale_line_id.product_id.id if self.sale_line_id else False,
                'default_salesperson_id': self.sale_line_id.order_id.user_id.id if self.sale_line_id and self.sale_line_id.order_id else False,
                'default_sale_order_date': self.sale_line_id.order_id.date_order if self.sale_line_id and self.sale_line_id.order_id else False,
                'default_project_manager_id': self.user_id.id if self.user_id else False,
                'default_audit_lead_id': self.audit_lead.id if self.audit_lead else False,
                'default_lead_status_id': self.lead_status.id if self.lead_status else False,
                'default_fees': self.sale_line_id.price_subtotal if self.sale_line_id else 0,
            },
        }
