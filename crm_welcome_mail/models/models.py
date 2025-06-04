from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MailDataSent(models.Model):
    _name = 'sent.mail.details'

    salesperson_name = fields.Many2one('res.users', string="Salesperson", tracking=True)
    designation = fields.Char(string="Designation", tracking=True)
    phone = fields.Char(string="Mobile/Phone Number", tracking=True)
    email = fields.Char(string="Email Address", tracking=True)
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, required=True)

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.env.company.id)
        if self.search_count([('company_id', '=', company_id)]) >= 1:
            raise ValidationError("Only one record can be created per company for Sent Mail Details.")
        return super(MailDataSent, self).create(vals)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model_create_multi
    def create(self, vals_list):
        leads = super(CrmLead, self).create(vals_list)
        for lead in leads:
            if lead.type == 'lead':
                self.send_welcome_email(lead)
        return leads

    def send_welcome_email(self, lead):
        mail_data = self.env['sent.mail.details'].search([('company_id', '=', self.env.company.id)], limit=1)

        if not mail_data:
            mail_data = self.env['sent.mail.details'].search([], limit=1)
            if not mail_data:
                return

        email_body = f"""
            <p>Dear {lead.name},</p>
            <p>I hope this message finds you well. </p>
            <p>My name is {mail_data.salesperson_name.name}, and I am your dedicated consultant at Analytix Management Consultancy. Thank you for considering us as your trusted partner in achieving your business goals. Your inquiry means a lot to us, and we are excited about the opportunity to collaborate with you.</p>
            <p>What's Next? </p>
            <p>We'll get back to you within the next 8 working hours to better understand your needs and provide tailored solutions.</p> <p>In the meantime, here's a quick overview of how we can support your business:</p>
            <ul>
                <li><strong>Business Setup:</strong> Streamlined solutions for entering Saudi Arabia or expanding globally.</li>
                <li><strong>Audit & Assurance:</strong> Building trust with stakeholders through meticulous audits.</li>
                <li><strong>Management Consulting:</strong> Strategic insights to optimize operations and drive growth.</li>
                <li><strong>Premium Residency:</strong> Unlock opportunities in Saudi Arabia with exclusive residency benefits.</li>
                <li><strong>PRO/GRO Services:</strong> Simplifying compliance and fostering government relationships.</li>
                <li><strong>Accounting & Taxation:</strong> Cutting-edge financial management solutions.</li>
            </ul>
            <p>You can learn more about our expertise by visiting our website: <a href="http://www.analytix.sa">www.analytix.sa</a> . Additionally, I've attached our Business Profile for your reference.</p>
            <p><strong>Why Choose Analytix?</strong></p>
            <p>With 16+ years of experience, a presence in 8+ countries , and a team of 200+ experts , we deliver end-to-end solutions tailored to your needs. Whether you're starting a new venture or scaling an existing one, we're here to guide you every step of the way.</p>
            <p>For seamless communication, I'll reach out to you shortly at {lead.phone or '-'} or via email at {lead.email_from}. If these details are incorrect or if you'd prefer alternate contact information, please let me know.</p>
            <p>Thank you once again for choosing Analytix . We look forward to helping you achieve your business goals.</p>
            <p>Best regards,</p>
            <p>{mail_data.salesperson_name.name}<br/>
           {mail_data.designation}<br/>
            Phone: {mail_data.phone}<br/>
           Email: {mail_data.email}<br/>
            {mail_data.company_id.name or 'Analytix'}<br/>
            Web: <a href="http://www.analytix.sa">www.analytix.sa</a></p>
            <br/>
            <div style="text-align: left; margin-bottom: 20px;">
                <img src="https://analytixtech.io/emailsign/analytix_logo_reveal.gif" alt="Analytix Logo" style="max-width: 200px;">
            </div>
             
            <p>___________________________________________</p>
        """

        mail = self.env['mail.mail'].sudo().create({
            'subject': 'Welcome to Analytix – Lets get you started!',
            'body_html': email_body,
            'email_from': 'CRM | Analytix',
            'email_to': lead.email_from,
            'reply_to': 'info@analytix.sa',
            'email_cc': mail_data.email,
            'auto_delete': True,
            'attachment_ids': [(6, 0, mail_data.attachment_ids.ids)] if mail_data.attachment_ids else False,
        })

        mail.send()
