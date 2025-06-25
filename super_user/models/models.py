from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    generate_reference_no = fields.Boolean(string="Generate Ref.No.")

    @api.model
    def create(self, values):
        print(values, ">>>>>Values from Zapier\n\n")

        user = self.env.user
        # Find the user Decord for Neil Antony Pinheiro
        neil_user = self.env['res.users'].search([('email', '=', 'neil@analytix.org')], limit=1)
        if not values.get('user_id', False) or values.get('user_id', 0) == 0:
            values['user_id'] = neil_user.ids[0]
        if not neil_user:
            raise UserError("User with email 'neil@analytix.org' not found.")

        return super(CrmLead, self).create(values)

    def write(self, vals):

        res = super(CrmLead, self).write(vals)


        if 'user_id' in vals:
            for lead in self:

                if lead.type == 'opportunity':

                    quotations = self.env['sale.order'].search([
                        ('opportunity_id', '=', lead.id),
                        ('state', 'in', ['draft', 'sent'])
                    ])


                    if quotations:
                        quotations.write({
                            'user_id': vals['user_id']
                        })


                        message = f"Salesperson changed to {self.env['res.users'].browse(vals['user_id']).name}. " \
                                  f"Updated {len(quotations)} quotation(s) with the new salesperson."
                        lead.message_post(body=message)

        return res

    def button_generate_reference_no(self):
        for record in self:

            if record.type == 'lead' and record.reference_no in ['/', 'NA']:

                if not record.campaign_id:
                    raise UserError("Please select a campaign before generating the reference number.")
                if not record.country_id:
                    raise UserError("Please select a country before generating the reference number.")

                crm_sequence = self.env['ir.sequence'].next_by_code('crm.lead.seq') or ''
                campaign = record.campaign_id
                country = record.country_id

                if country and country.code:
                    crm_sequence = country.code + crm_sequence
                if campaign and campaign.campaign_code:
                    crm_sequence = campaign.campaign_code + crm_sequence

                record.reference_no = crm_sequence
                record.generate_reference_no = True

    is_pushed_to_opp = fields.Boolean(string="Pushed to CRM")
    has_duplicate_lead = fields.Boolean(string="Duplicate Lead", compute="_check_if_duplicates", store=True)

    def push_to_opp(self):
        crm_lead_object = self.env['crm.lead']
        specific_stage = self.env['crm.stage'].search([('name', '=', 'Marketing Qualified Lead')], limit=1)
        if not specific_stage:
            raise ValidationError("The specific pipeline stage was not found.")

        for lead in self:
            if not lead.generate_reference_no or lead.reference_no in ['/', 'NA']:
                raise UserError("You must generate the reference number before pushing the lead to the pipeline.")

            crm_lead_vals = {
                'type': 'opportunity',
                'name': lead.name,
                'phone': lead.phone,
                'email_from': lead.email_from,
                'partner_name': lead.partner_name,
                'city': lead.city,
                'country_id': lead.country_id.id if lead.country_id else False,
                'user_id': lead.user_id.id if lead.user_id else False,
                'description': lead.description,
                'lead_owner_id': lead.lead_owner_id.id if lead.lead_owner_id else False,
                'campaign_id': lead.campaign_id.id if lead.campaign_id else False,
                'medium_id': lead.medium_id.id if lead.medium_id else False,
                'source_id': lead.source_id.id if lead.source_id else False,
                'assigned_date': lead.assigned_date,
                'tag_ids': lead.tag_ids.ids,
                'final_status': lead.final_status,
                'additional_comment': lead.additional_comment,
                'reference_no': lead.reference_no,
                'stage_id': specific_stage.id,
                'has_duplicate_lead': False,

            }

            crm_lead = crm_lead_object.create(crm_lead_vals)

            if not crm_lead:
                _logger.error(f"Failed to create CRM lead for lead ID {lead.id}")
                raise ValidationError("Failed to create CRM lead.")

            _logger.info(f"CRM lead created successfully for lead ID {lead.id}. CRM Lead ID: {crm_lead.id}")

            note = f"Lead pushed to CRM. CRM Lead ID: {crm_lead.id}, Pipeline Stage: {specific_stage.name}"
            lead.message_post(body=note)
            lead.is_pushed_to_opp = True
            lead.has_duplicate_lead = False
