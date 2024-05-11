from odoo import models, fields, api

from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class LinkWebsite(models.Model):
    _name = 'link_website.link_website'
    _description = 'Website Lead'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email ID")
    msg = fields.Char(string="Message")
    url = fields.Char(string="URL Link")
    sub = fields.Char(string="Subject")
    country = fields.Many2one('res.country', 'Country')
    serial_number = fields.Char(string="Serial Number", readonly=True, copy=False)
    lead_owner = fields.Many2one('res.users', 'Lead Owner', tracking=True)
    campaign = fields.Many2one('utm.campaign', 'Campaign', tracking=True)
    final = fields.Selection(
        [('hot', 'Hot'), ('cold', 'Cold'), ('warm', 'Warm'), ('qualified', 'Qualified'), ('lost', 'Lost'),
         ('no_response', 'No Response')], string='Lead Quality', tracking=True)
    assign_date = fields.Date(string='Assign a Date')
    user = fields.Many2one('res.users', string="Assigned To", tracking=True)
    is_pushed_web_to_crm = fields.Boolean(string="Pushed to CRM")

    @api.model
    def create(self, vals):
        if vals.get('serial_number') is None or vals.get('serial_number') == '/':
            vals['serial_number'] = self.env['ir.sequence'].next_by_code('link_website.serial') or '/'
        return super(LinkWebsite, self).create(vals)

    def push_web_to_crm(self):

        crm_lead_obj = self.env['crm.lead']

        for lead in self:
            user_name = lead.user.id if lead.user else False
            country_name = lead.country.id if lead.country else False

            # Create a CRM lead based on the website lead data
            crm_lead_vals = {
                'type': 'opportunity',
                'name': lead.name,
                'phone': lead.phone,
                'email_from': lead.email,
                'country_id': country_name,
                'description': f"Subject: {lead.sub}",
                'additional_comment': f"Message: {lead.msg}",
                'campaign_id': lead.campaign.id if lead.campaign else False,
                'user_id': user_name,
                'lead_owner_id': lead.lead_owner.id if lead.lead_owner else False,
                'final_status': lead.final,
                'assigned_date': lead.assign_date,
                # Add more fields as needed
            }

            # Create the CRM lead
            crm_lead = crm_lead_obj.create(crm_lead_vals)

            # Check if CRM lead creation was successful
            if not crm_lead:
                _logger.error(f"Failed to create CRM lead for lead ID {lead.id}")
                raise ValidationError("Failed to create CRM lead.")
            # Log a message indicating successful lead creation
            _logger.info(f"CRM lead created successfully for lead ID {lead.id}. CRM Lead ID: {crm_lead.id}")
            #         # Optionally, you can log a message or perform other actions
            note = f"Lead pushed to CRM. CRM Lead ID: {crm_lead.id}"
            lead.message_post(body=note)
            lead.is_pushed_web_to_crm = True
