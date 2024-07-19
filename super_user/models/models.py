from odoo import models, fields, api
from odoo.exceptions import UserError


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

    def button_generate_reference_no(self):
        for record in self:
            if record.type == 'lead' and record.reference_no in ['/', 'NA']:
                crm_sequence = self.env['ir.sequence'].next_by_code('crm.lead.seq') or ''
                campaign = self.env['utm.campaign'].sudo().browse(int(record.campaign_id.id))
                country = self.env['res.country'].sudo().browse(int(record.country_id.id))
                if country and country.code:
                    crm_sequence = country.code + crm_sequence
                if campaign and campaign.campaign_code:
                    crm_sequence = campaign.campaign_code + crm_sequence
                record.reference_no = crm_sequence
