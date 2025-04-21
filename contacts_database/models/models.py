from odoo import models, fields, api

from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class DatabaseName(models.Model):
    _name = 'database.name'

    name = fields.Char(string='Database Name')


class DatabasePaymentTerms(models.Model):
    _name = 'database.payment'

    name = fields.Char(string='Payment Terms')


class ContactsDatabase(models.Model):
    _name = 'contacts.database'
    _description = 'Customer Database'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    user = fields.Many2one('res.users', string="Created by", tracking=True, default=lambda self: self.env.user)
    assigned_rep = fields.Many2one('res.users', string="Assigned Sales Rep", tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    name = fields.Char(string="Client/Company Name", tracking=True)
    phone = fields.Char(string="Mobile/Phone Number", tracking=True)
    email = fields.Char(string="Email Address", tracking=True)
    job_position = fields.Char(string="Job Position/Designation", tracking=True)
    company_name = fields.Char(string="Company Name", tracking=True)
    country = fields.Many2one('res.country', 'Country', tracking=True)
    website_name = fields.Char(string="Company Website URL", tracking=True)
    tags_used = fields.Many2many('crm.tag', string="Service Interest", tracking=True)
    client_type = fields.Selection([
        ('new client', 'New Client'),
        ('existing client', 'Existing Client'),
    ], string="Client type", tracking=True)

    database_name = fields.Many2one('database.name', string="Database Name", tracking=True)
    database_source = fields.Many2one('utm.source', string="Lead Source", tracking=True)
    feedback = fields.Html(string='Custom Notes')
    verified = fields.Boolean(string='Data Verification', tracking=True)
    serial_number = fields.Char(string="Database Ref ID", readonly=True, copy=False)
    whatsapp_no = fields.Char(string='WhatsApp Number', tracking=True)
    linkedin_url = fields.Char(string='LinkedIn Profile URL', tracking=True)
    industry_type = fields.Char(string='Industry Type', tracking=True)
    company_size = fields.Integer(string='Company Size', tracking=True)
    business_type = fields.Many2many('res.partner.category', string="Business Type", tracking=True)
    city = fields.Char(string='City', tracking=True)
    acq_date = fields.Date(string='Acquisition Date', tracking=True)
    camp_source = fields.Many2one('utm.medium', string="Campaign Medium", tracking=True)
    ref_partner = fields.Char(string='Referral Partner', tracking=True)
    ext_service = fields.Char(string='Existing Services Availed', tracking=True)
    service_start = fields.Date(string='Service Start Date', tracking=True)
    service_end = fields.Date(string='Service End Date', tracking=True)
    inquiries = fields.Char(string='Past Inquiries/Requests', tracking=True)
    payment_terms = fields.Many2one('database.payment', string='Payment Terms')
    related_service = fields.Char(string='Related Services of Interest', tracking=True)
    previous_cross_sell = fields.Char(string='Previous Cross-Sell Attempts', tracking=True)
    customer_category = fields.Selection([
        ('new', 'New'), ('active', 'Active'), ('dormant', 'Dormant'), ('expired', 'Expired'),
        ('cancelled', 'Cancelled'), ('hold', 'Hold')
    ], string="Customer Category", tracking=True)
    engagement_source = fields.Selection([
        ('high', 'High'), ('medium', 'Medium'), ('low', 'Low')
    ], string="Engagement Score", tracking=True)
    marketing_consent = fields.Boolean(string='Marketing Consent', tracking=True)
    newsletter_sub = fields.Boolean(string='Newsletter Subscription', tracking=True)
    event_participation = fields.Char(string='Event Participation', tracking=True)
    last_contacted = fields.Date(string='Last Contacted Date', tracking=True)
    next_followup = fields.Date(string='Next Follow-Up Date', tracking=True)
    priority_level = fields.Selection([
        ('high', 'High'), ('medium', 'Medium'), ('low', 'Low')
    ], string="Priority Level", tracking=True)
    preferred_communication = fields.Many2one('communication.channel', string="Preferred Communication Channel",
                                              tracking=True)
    key_decision = fields.Boolean(string='Key Decision-Maker', tracking=True)
    data_score = fields.Float(string='Data Completeness Score', tracking=True)

    assign_date = fields.Date(string='Created Date', default=fields.Date.today)
    final = fields.Selection(
        [('hot', 'Hot'), ('cold', 'Cold'), ('warm', 'Warm'), ('qualified', 'Qualified'), ('lost', 'Lost'),
         ('no_response', 'No Response')], string='Lead Status', default='qualified', tracking=True)
    lead_owner = fields.Many2one('res.users', string='Lead Owner', tracking=True, default=lambda self: self.env.user)
    campaign = fields.Many2one('utm.campaign', 'Campaign', tracking=True)

    is_pushed_to_crm = fields.Boolean(string="Pushed to CRM")

    similar_data_exists = fields.Boolean(string="Similar Leads", compute='_compute_similar_data_exists', store=True)

    @api.depends('phone', 'email', 'whatsapp_no')
    def _compute_similar_data_exists(self):
        for record in self:
            domain = []
            if record.phone and record.phone != 'Nil':
                domain.append(('phone', '=', record.phone))
            if record.email and record.email != 'Nil':
                domain.append(('email', '=', record.email))
            if record.whatsapp_no and record.whatsapp_no != 'Nil':
                domain.append(('whatsapp_no', '=', record.whatsapp_no))

            if domain:
                domain = ['|'] * (len(domain) - 1) + domain
                similar_records = self.search(domain).filtered(lambda r: r.id != record.id)
                record.similar_data_exists = bool(similar_records)
            else:
                record.similar_data_exists = False

    @api.model
    def create(self, vals):
        if not vals.get('serial_number') or vals.get('serial_number') == '/':
            vals['serial_number'] = self.env['ir.sequence'].next_by_code('contacts_database.serial') or '/'
        return super(ContactsDatabase, self).create(vals)

    def push_to_crm(self):
        crm_lead_obj = self.env['crm.lead']
        pushed_leads = []
        default_user = self.env['res.users'].search([('login', '=', 'sreelekha@analytix.org')], limit=1)
        if not default_user:
            raise ValidationError("Default user 'Sreelekha' not found. Please check the username.")
        default_campaign = self.env['utm.campaign'].search([('name', '=', 'Offline')], limit=1)
        if not default_campaign:
            raise ValidationError("Check Campaign!")

        default_medium = self.env['utm.medium'].search([('name', '=', 'Contacts Database')], limit=1)
        if not default_medium:
            raise ValidationError("Check Medium!")
        for lead in self:
            if lead.is_pushed_to_crm:
                continue

            country_name = lead.country.id if lead.country else False
            user_name = lead.user.id if lead.user else False
            _logger.info(f"Creating CRM lead for lead ID {lead.id} with user ID {user_name}")
            source_name = lead.database_name.name if lead.database_name else False
            source_id = False
            if source_name:
                existing_source = self.env['utm.source'].search([('name', '=', source_name)], limit=1)
                if existing_source:
                    source_id = existing_source.id
                else:
                    raise ValidationError("Check Source!")

            crm_lead_vals = {
                'type': 'opportunity',
                'name': lead.name,
                'contact_name': lead.name,
                'partner_name': lead.company_name,
                'phone': lead.phone,
                'mobile': lead.whatsapp_no,
                'website': lead.website_name,
                'tag_ids': [(6, 0, lead.tags_used.ids)] if lead.tags_used else False,
                'email_from': lead.email,
                'description': lead.feedback,
                'street': lead.city,
                'country_id': country_name,
                'user_id': lead.assigned_rep.id if lead.assigned_rep else default_user.id,
                'lead_owner_id': lead.lead_owner.id if lead.lead_owner else False,
                'campaign_id': lead.campaign.id if lead.campaign else default_campaign.id,
                'medium_id': lead.camp_source.id if lead.camp_source else default_medium.id,
                'source_id': source_id,
                'assigned_date': lead.assign_date,
                'final_status': lead.final or 'qualified',
                'function': lead.job_position,
            }
            crm_lead = crm_lead_obj.create(crm_lead_vals)

            if not crm_lead:
                _logger.error(f"Failed to create CRM lead for lead ID {lead.id}")
                raise ValidationError("Failed to create CRM lead.")

            _logger.info(f"CRM lead created successfully for lead ID {lead.id}. CRM Lead ID: {crm_lead.id}")

            note = f"Lead pushed to CRM. CRM Lead ID: {crm_lead.id}"
            lead.message_post(body=note)
            lead.is_pushed_to_crm = True
            pushed_leads.append(lead.id)

        if len(pushed_leads) > 1:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'{len(pushed_leads)} leads have been pushed to CRM',
                    'sticky': False,
                    'type': 'success',
                }
            }

    def show_similar_data(self):

        self.ensure_one()

        domain = []
        if self.phone and self.phone != 'Nil':
            domain.append(('phone', '=', self.phone))
        if self.email and self.email != 'Nil':
            domain.append(('email', '=', self.email))
        if self.whatsapp_no and self.whatsapp_no != 'Nil':
            domain.append(('whatsapp_no', '=', self.whatsapp_no))

        if domain:
            domain = ['|'] * (len(domain) - 1) + domain
        else:
            domain = [('id', '=', False)]

        similar_records = self.search(domain)
        _logger.info(f"Similar Records: {similar_records.ids}")

        return {

            'name': 'Similar Data',

            'type': 'ir.actions.act_window',

            'res_model': 'contacts.database',

            'view_mode': 'tree,form',

            'domain': [('id', 'in', similar_records.ids)],

        }
