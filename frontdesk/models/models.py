# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class frontdesk(models.Model):
    _name = 'frontdesk.frontdesk'
    _description = 'Walkin-Customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    user = fields.Many2one('res.users', string="Point of contact", tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    # start_date = fields.Datetime(string='Start Date', required=True)
    # end_date = fields.Datetime(string='End Date', required=True)
    name = fields.Char(string="Name")
    phone = fields.Char(string="Mobile Phone")
    email = fields.Char(string="Email ")
    org = fields.Char(string="Organization")
    country = fields.Many2one('res.country', 'Country')
    purpose = fields.Selection([
        ('meeting', 'Meetings'),
        ('interview', 'Interview'),
        ('payment and billing', 'Payment and Billing'),
        ('document submission', 'Document Submission'),
        ('general enquiry', 'General Enquiry'),
        ('maintenance', 'Maintenance'),
        ('delivery and pickup', 'Delivery and Pickup'),
        ('product and service enquiry', 'Product and Service Enquiry'),
        ('complaint', 'Complaint'),
        ('others', 'Others')
    ], string="Purpose of visit", tracking=True)
    service = fields.Selection([
        ('ksa foreign company formation', 'KSA Foreign Company Formation'),
        ('ksa gcc company formation', 'KSA GCC Company Formation'),
        ('pro/gro service', 'PRO/GRO Service'),
        ('trademark', 'Trademark'),
        ('post incorporation', 'Post Incorporation'),
        ('license amendment', 'License Amendment'),
        ('industrial license', 'Industrial License'),
        ('company takeover', 'Company Takeover'),
        ('premium residency', 'Premium Residency'),
        ('uae business incorporation', 'UAE Business incorporation'),
        ('accounting', 'Accounting'),
        ('taxation ', 'Taxation '),
        ('audit', 'Audit'),
        ('feasibility study', 'Feasibility Study'),
        ('ext-file', 'EXT-File'),
        ('others', 'Others')
    ], string="Service Interest", tracking=True)
    show_service = fields.Boolean(string="Show Service Field", compute='_compute_show_service')

    @api.depends('purpose')
    def _compute_show_service(self):
        for record in self:
            record.show_service = record.purpose == 'product and service enquiry'

    client_type = fields.Selection([
        ('new client', 'New Client'),
        ('existing client', 'Existing Client'),
    ], string="Client type", tracking=True)
    lead_owner = fields.Many2one('res.users', string='Lead Owner', tracking=True, default=lambda self: self.env.user)
    campaign = fields.Many2one('utm.campaign', 'Campaign', tracking=True, default=lambda self: self._default_campaign())
    final = fields.Selection(
        [('hot', 'Hot'), ('cold', 'Cold'), ('warm', 'Warm'), ('qualified', 'Qualified'), ('lost', 'Lost'),
         ('no_response', 'No Response')], string='Lead Quality', tracking=True, default='qualified')
    assign_date = fields.Date(string='Assigned Date', default=fields.Date.today)
    is_pushed_to_crm = fields.Boolean(string="Pushed to CRM")
    similar_data_exists = fields.Boolean(string="Similar Leads", compute='_compute_similar_data_exists', store=True)

    @api.depends('phone', 'email')
    def _compute_similar_data_exists(self):
        for record in self:
            domain = []
            if record.phone and record.phone != 'Nil':
                domain.append(('phone', '=', record.phone))
            if record.email and record.email != 'Nil':
                domain.append(('email', '=', record.email))

            if domain:
                domain = ['|'] * (len(domain) - 1) + domain
                similar_records = self.search(domain).filtered(lambda r: r.id != record.id)
                record.similar_data_exists = bool(similar_records)
            else:
                record.similar_data_exists = False

    @api.model
    def _default_campaign(self):
        return self.env['utm.campaign'].search([('name', '=', 'Offline')], limit=1).id

    def write(self, vals):

        old_values = {field: self._fields[field].convert_to_display_name(self[field], self) for field in vals.keys()}

        res = super(frontdesk, self).write(vals)

        for record in self:
            note = "Lead updated with changes:\n"
            for field, value in vals.items():
                if field in record._fields and record._fields[field].type != 'selection':
                    field_label = record._fields.get(field).string
                    old_value = old_values.get(field)
                    if record._fields[field].type == 'many2one':
                        new_value = record[field].display_name if record[field] else ''
                    elif record._fields[field].type == 'many2many' or record._fields[field].type == 'one2many':
                        new_value = ', '.join(record[field].mapped('display_name'))
                    else:
                        new_value = value
                    note += f"/{field_label}: {old_value} -> {new_value}\t/"
            record.message_post(body=note)
        return res

    def push_to_crm(self):
        crm_lead_obj = self.env['crm.lead']

        for lead in self:
            country_name = lead.country.id if lead.country else False
            user_name = lead.user.id if lead.user else False
            _logger.info(f"Creating CRM lead for lead ID {lead.id} with user ID {user_name}")

            crm_lead_vals = {
                'type': 'opportunity',
                'name': lead.name,
                'phone': lead.phone,
                'email_from': lead.email,
                'partner_name': lead.org,
                'country_id': country_name,
                'user_id': user_name,
                'description': f"Purpose of visit : {lead.purpose} - {lead.service}",
                'lead_owner_id': lead.lead_owner.id if lead.lead_owner else False,
                'campaign_id': lead.campaign.id if lead.campaign else False,
                'assigned_date': lead.assign_date,
                'final_status': lead.final,

            }

            crm_lead = crm_lead_obj.create(crm_lead_vals)

            if not crm_lead:
                _logger.error(f"Failed to create CRM lead for lead ID {lead.id}")
                raise ValidationError("Failed to create CRM lead.")

            _logger.info(f"CRM lead created successfully for lead ID {lead.id}. CRM Lead ID: {crm_lead.id}")

            note = f"Lead pushed to CRM. CRM Lead ID: {crm_lead.id}"
            lead.message_post(body=note)
            lead.is_pushed_to_crm = True

    serial_number = fields.Char(string="Serial Number", readonly=True, copy=False)

    @api.model
    def create(self, vals):
        if vals.get('serial_number') is None or vals.get('serial_number') == '/':
            vals['serial_number'] = self.env['ir.sequence'].next_by_code('frontdesk.serial') or '/'

        if not vals.get('assign_date'):
            vals['assign_date'] = fields.Date.today()

        if not vals.get('lead_owner'):
            vals['lead_owner'] = self.env.user.id

        leads = super(frontdesk, self).create(vals)

        for lead in leads:
            note = "New Lead created with Consultant: {}".format(
                ', '.join(lead.user.mapped('name')))
            lead.message_post(body=note)

        return leads

    def show_similar_data(self):

        self.ensure_one()

        domain = []
        if self.phone and self.phone != 'Nil':
            domain.append(('phone', '=', self.phone))
        if self.email and self.email != 'Nil':
            domain.append(('email', '=', self.email))

        if domain:
            domain = ['|'] * (len(domain) - 1) + domain
        else:
            domain = [('id', '=', False)]

        similar_records = self.search(domain)
        _logger.info(f"Similar Records: {similar_records.ids}")

        return {

            'name': 'Similar Data',

            'type': 'ir.actions.act_window',

            'res_model': 'frontdesk.frontdesk',

            'view_mode': 'tree,form',

            'domain': [('id', 'in', similar_records.ids)],

        }

    def set_similar_data_false(self):
        for record in self:
            record.similar_data_exists = False
