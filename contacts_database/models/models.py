from odoo import models, fields, api

from odoo.exceptions import ValidationError
import logging
import requests

_logger = logging.getLogger(__name__)


class contactsdatabase(models.Model):
    _name = 'contacts.database'
    _description = 'Customer Database'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'company_name'

    user = fields.Many2one('res.users', string="Point of contact", tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    name = fields.Char(string="Client Name", tracking=True)
    phone = fields.Char(string="Mobile/Phone Number", tracking=True)
    email = fields.Char(string="Email", tracking=True)
    job_position = fields.Char(string="Job Position", tracking=True)
    address = fields.Char(string="Address", tracking=True)
    company_name = fields.Char(string="Company Name", tracking=True)
    country = fields.Many2one('res.country', 'Country', tracking=True, default=lambda self: self._default_country())
    location = fields.Char(string="Location", tracking=True)
    website_name = fields.Char(string="Website", tracking=True)
    tags_used = fields.Many2many('crm.tag', string="Service Interest", tracking=True)

    assign_date = fields.Date(string='Assigned Date', default=fields.Date.today)
    final = fields.Selection(
        [('hot', 'Hot'), ('cold', 'Cold'), ('warm', 'Warm'), ('qualified', 'Qualified'), ('lost', 'Lost'),
         ('no_response', 'No Response')], string='Lead Quality', tracking=True, default='qualified')
    lead_owner = fields.Many2one('res.users', string='Lead Owner', tracking=True, default=lambda self: self.env.user)
    campaign = fields.Many2one('utm.campaign', 'Campaign', tracking=True, default=lambda self: self._default_campaign())

    is_pushed_to_crm = fields.Boolean(string="Pushed to CRM")
    is_location_fetched = fields.Boolean(string="Fetched Location")
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

    def _default_country(self):
        return self.env['res.country'].search([('name', '=', 'Saudi Arabia')], limit=1).id

    def push_to_crm(self):
        crm_lead_obj = self.env['crm.lead']

        for lead in self:
            country_name = lead.country.id if lead.country else False
            user_name = lead.user.id if lead.user else False
            _logger.info(f"Creating CRM lead for lead ID {lead.id} with user ID {user_name}")

            crm_lead_vals = {
                'type': 'opportunity',
                'name': lead.company_name,
                'contact_name': lead.name,
                'phone': lead.phone,
                'website': lead.website_name,
                'tag_ids': [(6, 0, lead.tags_used.ids)] if lead.tags_used else False,
                'email_from': lead.email,
                'street': lead.address,
                'street2': lead.location,
                'country_id': country_name,
                'user_id': user_name,
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

            'res_model': 'contacts.database',

            'view_mode': 'tree,form',

            'domain': [('id', 'in', similar_records.ids)],

        }

    def set_similar_data_false(self):
        for record in self:
            record.similar_data_exists = False

    def fetch_current_location(self):
        """Fetch the current location using a geolocation API."""
        try:
            response = requests.get('http://ip-api.com/json/')
            if response.status_code == 200:
                data = response.json()
                self.location = f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}"
                _logger.info(f"Location fetched successfully: {self.location}")
            else:
                _logger.error("Failed to fetch location: Invalid response from API.")
                raise ValidationError("Unable to fetch location at this time. Please try again later.")
        except Exception as e:
            _logger.error(f"Error fetching location: {e}")
            raise ValidationError("An error occurred while fetching the location.")

        for lead in self:
            lead.is_location_fetched = True
