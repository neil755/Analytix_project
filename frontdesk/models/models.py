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

    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    name = fields.Char(string="Name")
    phone = fields.Char(string="Mobile Phone")
    email = fields.Char(string="Email ")
    org = fields.Char(string="Organization")
    country = fields.Many2one('res.country', 'Country')
    purpose = fields.Selection([
        ('business setup', 'Business Setup'),
        ('pro', 'PRO'),
        ('amendments', 'Amendments'),
        ('audit', 'Audit'),
        ('f&a', 'F&A'),
        ('operations', 'Operations'),
        ('phase 3', 'Phase 3'),
        ('trademark', 'Trademark'),
        ('mgt.consulting', 'MGT.Consulting'),
        ('accounting service', 'Accounting Service'),
        ('others', 'Others')
    ], string="Purpose of visit", tracking=True)

    type = fields.Selection([
        ('service license', 'Service License'),
        ('entrepreneurial license', 'Entrepreneurial License'),
        ('industrial license', 'Industrial License'),
        ('agricultural license', 'Agricultural License'),
        ('real estate license', 'Real Estate License'),
        ('mining license', 'Mining License'),
        ('professional license', 'Professional License'),
        ('trading license', 'Trading License'),
        ('others', 'Others')
    ], string="Type of license", tracking=True)
    client_type = fields.Selection([
        ('new client', 'New Client'),
        ('existing client', 'Existing Client'),
    ], string="Client type", tracking=True)
    lead_owner = fields.Many2one('res.users', 'Lead Owner', tracking=True)
    campaign = fields.Many2one('utm.campaign', 'Campaign', tracking=True)
    final = fields.Selection(
        [('hot', 'Hot'), ('cold', 'Cold'), ('warm', 'Warm'), ('qualified', 'Qualified'), ('lost', 'Lost'),
         ('no_response', 'No Response')], string='Lead Quality', tracking=True)

    def write(self, vals):
        # Fetch the old values before the write operation
        old_values = {field: self._fields[field].convert_to_display_name(self[field], self) for field in vals.keys()}

        # Call the superclass write method to perform the write operation
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



            # Create a CRM lead based on the frontdesk lead data
            crm_lead_vals = {
                'name': lead.name,
                'phone': lead.phone,
                'email_from': lead.email,
                'partner_name': lead.org,
                'country_id': country_name,
                'user_id': user_name,
                'description': f"Purpose of visit: {lead.purpose}",
                'lead_owner_id': lead.lead_owner.id if lead.lead_owner else False,
                'campaign_id': lead.campaign.id if lead.campaign else False,
                'final_status': lead.final,  # Correctly assigning the display value
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
            # Optionally, you can log a message or perform other actions
            note = f"Lead pushed to CRM. CRM Lead ID: {crm_lead.id}"
            lead.message_post(body=note)

    serial_number = fields.Char(string="Serial Number", readonly=True, copy=False)

    @api.model
    def create(self, vals):
        if vals.get('serial_number') is None or vals.get('serial_number') == '/':
            vals['serial_number'] = self.env['ir.sequence'].next_by_code('frontdesk.serial') or '/'

        leads = super(frontdesk, self).create(vals)

        for lead in leads:
            note = "New Lead created with Consultant: {}".format(
                ', '.join(lead.user.mapped('name')))
            lead.message_post(body=note)

        return leads
