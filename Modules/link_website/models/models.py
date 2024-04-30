from odoo import models, fields, api


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
    serial_number = fields.Char(string="Serial Number", readonly=True, copy=False)

    @api.model
    def create(self, vals):
        if vals.get('serial_number') is None or vals.get('serial_number') == '/':
            vals['serial_number'] = self.env['ir.sequence'].next_by_code('link_website.serial') or '/'
        return super(LinkWebsite, self).create(vals)

