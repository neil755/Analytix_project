from odoo import models, fields, api
from datetime import date
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
    _rec_name = 'partner_id'

    name = fields.Char(string='Client Code', tracking=True)
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
    tag_ids = fields.Many2many('project.tags', string='Audit Period',
                               compute='_compute_tag_ids',
                               store=True, tracking=True)

    engagement_sign_date = fields.Date(string='Engagement Signing Date', tracking=True)
    payment_followup_assign_id = fields.Many2one('res.users', string='Payment Followup Assigned To', tracking=True)
    fees = fields.Float(string='Fees', compute='_compute_fee_amount', store=True)
    tax_payment = fields.Float(string='Tax Payment Amount')
    tax_payment_conf = fields.Boolean(string='Tax Payment Amount Confirmation')
    first_payment = fields.Float(string='First Payment Amount')
    first_payment_conf = fields.Boolean(string='First Payment Amount Confirmation')
    first_payment_status = fields.Many2one('audit.payment.status', tracking=True)
    first_payment_received_date = fields.Date(string='First Payment Received Date', tracking=True)
    second_payment = fields.Float(string='Second Payment Amount')
    second_payment_conf = fields.Boolean(string='Second Payment Amount Confirmation')
    second_payment_status = fields.Many2one('audit.payment.status', tracking=True)
    second_payment_received_date = fields.Date(string='Second Payment Received Date', tracking=True)
    final_payment = fields.Float(string='Final Payment Amount')
    final_payment_conf = fields.Boolean(string='Final Payment Amount Confirmation')
    final_payment_status = fields.Many2one('audit.payment.status', tracking=True)
    final_payment_received_date = fields.Date(string='Final Payment Received Date', tracking=True)

    assigned_to_id = fields.Many2one('res.users', string='Assigned To', tracking=True)
    audit_status = fields.Many2one('audit.review.status', string='Audit Requirements Status', tracking=True)
    audit_req_sharing_date = fields.Date(string='Audit Requirements Sharing Date', tracking=True)
    tb_receive_date = fields.Date(string='TB/BIS Receiving Date', tracking=True)
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
    initial_complete_date = fields.Date(string='Initial Review Completed Date', tracking=True)
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
    manager_analytix_date = fields.Date(string='Date of Completion of Manager Review ',
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

    has_similar_projects = fields.Boolean(
        string='Has Similar Projects',
        compute='_compute_has_similar_projects',
        store=True
    )

    @api.depends('project_id')
    def _compute_has_similar_projects(self):
        for record in self:

            if isinstance(record.id, models.NewId):
                record.has_similar_projects = False
                continue

            if record.project_id:
                similar_projects = self.search_count([
                    ('project_id', '=', record.project_id.id),
                    ('id', '!=', record.id)
                ])
                record.has_similar_projects = similar_projects > 0
            else:
                record.has_similar_projects = False



    received_document_ids = fields.One2many(
        'project.custom',
        compute='_compute_received_document_ids',
        string='List view of Received Documents'
    )

    pending_document_ids = fields.One2many(
        'project.custom',
        compute='_compute_pending_document_ids',
        string='List View of Pending Documents'
    )

    @api.depends('project_id')
    def _compute_received_document_ids(self):
        for record in self:
            if record.project_id:
                record.received_document_ids = self.env['project.custom'].search([
                    ('project_id', '=', record.project_id.id),
                    ('status_type', '=', 'Received')
                ])
            else:
                record.received_document_ids = False

    @api.depends('project_id')
    def _compute_pending_document_ids(self):
        for record in self:
            if record.project_id:
                record.pending_document_ids = self.env['project.custom'].search([
                    ('project_id', '=', record.project_id.id),
                    ('status_type', '=', 'Pending')
                ])
            else:
                record.pending_document_ids = False

    no_days_fees = fields.Float(string='No. of Days in Fees', compute="_compute_no_days_fees", store=False)

    @api.depends('audit_req_sharing_date', 'first_payment_received_date')
    def _compute_no_days_fees(self):
        for record in self:

            audit_req_sharing_date = record.audit_req_sharing_date or date.today()

            if audit_req_sharing_date and record.first_payment_received_date:

                if audit_req_sharing_date >= record.first_payment_received_date:
                    delta = audit_req_sharing_date - record.first_payment_received_date
                    record.no_days_fees = delta.days
                else:

                    record.no_days_fees = 0
            else:

                record.no_days_fees = 0

    no_days_initial = fields.Float(string='No. of Days in Initial Audit', compute="_compute_no_days_initial",
                                   store=False)

    @api.depends('tb_receive_date', 'audit_req_sharing_date')
    def _compute_no_days_initial(self):
        for record in self:
            if record.tb_receive_date and record.audit_req_sharing_date:
                if record.tb_receive_date >= record.audit_req_sharing_date:
                    delta = record.tb_receive_date - record.audit_req_sharing_date
                    record.no_days_initial = delta.days
                else:

                    record.no_days_initial = 0
            else:

                record.no_days_initial = 0

    no_days_tb = fields.Float(string='No. of Days in TB', compute="_compute_no_days_tb",
                              store=False)

    @api.depends('initial_review_date', 'last_audit_receiving_date')
    def _compute_no_days_tb(self):
        for record in self:
            if record.initial_review_date and record.last_audit_receiving_date:
                if record.initial_review_date >= record.last_audit_receiving_date:
                    delta = record.initial_review_date - record.last_audit_receiving_date
                    record.no_days_tb = delta.days
                else:

                    record.no_days_tb = 0
            else:

                record.no_days_tb = 0

    no_days_analytix_first = fields.Float(string='No. of Days in Analytix First Review',
                                          compute="_compute_no_days_analytix_first",
                                          store=False)

    @api.depends('initial_complete_date', 'initial_review_date')
    def _compute_no_days_analytix_first(self):
        for record in self:
            if record.initial_complete_date and record.initial_review_date:
                if record.initial_complete_date >= record.initial_review_date:
                    delta = record.initial_complete_date - record.initial_review_date
                    record.no_days_analytix_first = delta.days
                else:

                    record.no_days_analytix_first = 0
            else:

                record.no_days_analytix_first = 0

    no_days_abcpa_first = fields.Float(string='No. of Days in ABCPA First Review',
                                       compute="_compute_no_days_abcpa_first",
                                       store=False)

    @api.depends('abcpa_complete_date', 'abcpa_review_date')
    def _compute_no_days_abcpa_first(self):
        for record in self:
            if record.abcpa_complete_date and record.abcpa_review_date:
                if record.abcpa_complete_date >= record.abcpa_review_date:
                    delta = record.abcpa_complete_date - record.abcpa_review_date
                    record.no_days_abcpa_first = delta.days
                else:

                    record.no_days_abcpa_first = 0
            else:

                record.no_days_abcpa_first = 0

    no_days_analytix_second = fields.Float(string='No. of Days in Analytix Second Review',
                                           compute="_compute_no_days_analytix_second",
                                           store=False)

    @api.depends('second_analytix_date', 'second_review_receive_date')
    def _compute_no_days_analytix_second(self):
        for record in self:
            if record.second_analytix_date and record.second_review_receive_date:
                if record.second_analytix_date >= record.second_review_receive_date:
                    delta = record.second_analytix_date - record.second_review_receive_date
                    record.no_days_analytix_second = delta.days
                else:

                    record.no_days_analytix_second = 0
            else:

                record.no_days_analytix_second = 0

    no_days_manager = fields.Float(string='No. of Days in Manager Review',
                                   compute="_compute_no_days_manager",
                                   store=False)

    @api.depends('manager_analytix_date', 'second_analytix_date')
    def _compute_no_days_manager(self):
        for record in self:
            if record.manager_analytix_date and record.second_analytix_date:
                if record.manager_analytix_date >= record.second_analytix_date:
                    delta = record.manager_analytix_date - record.second_analytix_date
                    record.no_days_manager = delta.days
                else:

                    record.no_days_manager = 0
            else:

                record.no_days_manager = 0

    no_days_abcpa_final = fields.Float(string='No. of Days in ABCPA Final',
                                       compute="_compute_no_days_abcpa_final",
                                       store=False)

    @api.depends('abcpa_final_reply_date', 'abcpa_final_receive_date')
    def _compute_no_days_abcpa_final(self):
        for record in self:
            if record.abcpa_final_reply_date and record.abcpa_final_receive_date:
                if record.abcpa_final_reply_date >= record.abcpa_final_receive_date:
                    delta = record.abcpa_final_reply_date - record.abcpa_final_receive_date
                    record.no_days_abcpa_final = delta.days
                else:

                    record.no_days_abcpa_final = 0
            else:

                record.no_days_abcpa_final = 0

    no_days_final = fields.Float(string='No. of Days in Final Audit',
                                 compute="_compute_no_days_final",
                                 store=False)

    @api.depends('final_receive_date', 'final_share_date')
    def _compute_no_days_final(self):
        for record in self:
            if record.final_receive_date and record.final_share_date:
                if record.final_receive_date >= record.final_share_date:
                    delta = record.final_receive_date - record.final_share_date
                    record.no_days_final = delta.days
                else:

                    record.no_days_final = 0
            else:

                record.no_days_final = 0

    no_days_zakat = fields.Float(string='No. of Days in ZAKAT Filing',
                                 compute="_compute_no_days_zakat",
                                 store=False)

    @api.depends('zakat_file_date', 'zakat_complete_date')
    def _compute_no_days_zakat(self):
        for record in self:
            if record.zakat_file_date and record.zakat_complete_date:
                if record.zakat_file_date >= record.zakat_complete_date:
                    delta = record.zakat_file_date - record.zakat_complete_date
                    record.no_days_zakat = delta.days
                else:

                    record.no_days_zakat = 0
            else:

                record.no_days_zakat = 0

    @api.depends('project_id')
    def _compute_partner_id(self):
        for record in self:
            record.partner_id = record.project_id.partner_id if record.project_id else False

    @api.depends('project_id')
    def _compute_project_manager_id(self):
        for record in self:
            record.project_manager_id = record.project_id.user_id if record.project_id else False

    @api.depends('project_id')
    def _compute_audit_lead_id(self):
        for record in self:
            record.audit_lead_id = record.project_id.audit_lead if record.project_id else False

    @api.depends('project_id')
    def _compute_lead_status_id(self):
        for record in self:
            record.lead_status_id = record.project_id.lead_status if record.project_id else False

    @api.depends('sale_line_id')
    def _compute_sale_order_date(self):
        for record in self:
            record.sale_order_date = record.sale_line_id.order_id.date_order if record.sale_line_id and record.sale_line_id.order_id else False

    @api.depends('sale_line_id')
    def _compute_salesperson_id(self):
        for record in self:
            record.salesperson_id = record.sale_line_id.order_id.user_id if record.sale_line_id and record.sale_line_id.order_id else False

    @api.depends('project_id')
    def _compute_tag_ids(self):
        for record in self:
            record.tag_ids = record.project_id.tag_ids if record.project_id else False

    @api.depends('project_id')
    def _compute_received_documents(self):
        for record in self:
            if record.project_id:
                # Count the number of documents with status 'Received'
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
                # Count the number of documents with status 'Pending'
                record.pending_documents = self.env['project.custom'].search_count([
                    ('project_id', '=', record.project_id.id),
                    ('status_type', '=', 'Pending')
                ])
            else:
                record.pending_documents = 0

    @api.depends('project_id', 'project_id.sale_line_id')
    def _compute_sale_line_id(self):
        for record in self:
            if record.project_id and record.project_id.sale_line_id:
                record.sale_line_id = record.project_id.sale_line_id
            else:
                record.sale_line_id = False

    @api.depends('sale_line_id', 'sale_line_id.product_id')
    def _compute_product_id(self):
        for record in self:
            if record.sale_line_id and record.sale_line_id.product_id:
                record.product_id = record.sale_line_id.product_id
            else:
                record.product_id = False

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
        self._compute_lead_status_id()
        self._compute_sale_line_id()
        self._compute_product_id()
        self._compute_fee_amount()
        self._compute_received_documents()
        self._compute_pending_documents()
        self._compute_received_document_ids()
        self._compute_pending_document_ids()

    def write(self, vals):
        res = super(AuditTracker, self).write(vals)
        if 'project_id' in vals:
            self._compute_project_manager_id()
            self._compute_audit_lead_id()
            self._compute_tag_ids()
            self._compute_lead_status_id()
            self._compute_sale_line_id()
            self._compute_product_id()
            self._compute_fee_amount()
            self._compute_received_documents()
            self._compute_pending_documents()
            self._compute_received_document_ids()
            self._compute_pending_document_ids()
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

    def action_show_received_documents(self):
        self.ensure_one()
        return {
            'name': 'Received Documents',
            'type': 'ir.actions.act_window',
            'res_model': 'project.custom',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.received_document_ids.ids)],
            'context': {'default_project_id': self.project_id.id,
                        'create': False,
                        'edit': False,
                        },
        }

    def action_show_pending_documents(self):
        self.ensure_one()
        return {
            'name': 'Pending Documents',
            'type': 'ir.actions.act_window',
            'res_model': 'project.custom',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.pending_document_ids.ids)],
            'context': {'default_project_id': self.project_id.id,
                        'create': False,
                        'edit': False,
                        },
        }


class ProjectAuditTracker(models.Model):
    _inherit = 'project.project'

    has_audit_tracker = fields.Boolean(
        string='Has Audit Tracker',
        compute='_compute_has_audit_tracker',
        store=True
    )
    audit_tracker_ids = fields.One2many(
        'audit.tracker',
        'project_id',
        string='Audit Trackers'
    )

    @api.depends('audit_tracker_ids')
    def _compute_has_audit_tracker(self):
        for record in self:

            record.has_audit_tracker = bool(record.audit_tracker_ids)



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
