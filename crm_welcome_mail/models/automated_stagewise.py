from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging
import traceback
from pytz import timezone, utc

_logger = logging.getLogger(__name__)


class AutomaticMailConfiguration(models.Model):
    _name = 'automatic.mail.config'
    _description = 'Automatic Mail Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'days_after asc'

    name = fields.Char(string='Name', required=True)
    stage_ids = fields.Many2many(
        'crm.stage',
        string='Applicable Stages',
        required=True,
        help="Stages where this automatic mail should be applied"
    )
    team_id = fields.Many2one(
        'crm.team',
        string='Sales Team Filter',
        help="Only apply to leads/opportunities in this sales team (leave empty for all teams)"
    )
    user_id = fields.Many2one(
        'res.users',
        string='Salesperson Filter',
        help="Only apply to leads/opportunities assigned to this user (leave empty for any user)"
    )
    final = fields.Selection(
        [
            ('hot', 'Hot'),
            ('cold', 'Cold'),
            ('warm', 'Warm'),
            ('qualified', 'Qualified'),
            ('lost', 'Lost'),
            ('no_response', 'No Response')
        ],
        string='Lead Quality Filter',
        help="Only apply to leads/opportunities with this quality (leave empty for any quality)"
    )
    days_after = fields.Integer(
        string='Days After Stage Entry',
        required=True,
        default=1,
        help="Number of full days after entering the stage to send the email"
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    tag_ids = fields.Many2many(
        'crm.tag',
        string='Tag Filter',
        help="Only apply to leads/opportunities with these tags (leave empty for any tags)"
    )
    active = fields.Boolean(string='Active', default=True)
    last_execution = fields.Datetime(
        string='Last Execution Time',
        readonly=True,
        help="When this configuration was last processed"
    )
    next_execution = fields.Datetime(
        string='Next Execution Time',
        compute='_compute_next_execution',
        store=True,
        help="When this configuration will be processed next"
    )
    lead_type = fields.Selection(
        [('opportunity', 'Opportunities Only')],
        string='Apply To',
        default='opportunity',
        required=True
    )

    subject = fields.Char(string='Email Subject', required=True)
    body_html = fields.Html(string='Email Body')
    email_from = fields.Char(string='From', help="Sender email address")
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")

    cc_emails = fields.Char(
        string='CC Emails',
        help="Comma-separated list of email addresses to carbon copy"
    )

    reply_to = fields.Char(
        string='Reply-To Email',
        help="Email address that should receive replies"
    )

    @api.constrains('days_after')
    def _check_days_after(self):
        for config in self:
            if config.days_after < 0:
                raise ValidationError(_("Days after stage entry must be a positive number"))

    @api.depends('last_execution')
    def _compute_next_execution(self):
        for config in self:
            if config.last_execution:
                config.next_execution = config.last_execution + timedelta(hours=1)
            else:
                config.next_execution = fields.Datetime.now()

    def send_test_emails(self):
        self.ensure_one()
        leads = self._get_leads_to_process(limit=5)
        if not leads:
            raise UserError(_("No matching leads/opportunities found for this configuration"))

        for lead in leads:
            self._send_email_to_lead(lead)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Test Emails Sent"),
                'message': _("Test emails have been sent to %d matching leads/opportunities.") % len(leads),
                'sticky': False,
            }
        }

    @api.model
    def _cron_send_automatic_mails(self):
        configs = self.search([('active', '=', True)])
        _logger.info("Starting automatic mail processing for %d configurations", len(configs))

        for config in configs:
            try:
                _logger.info("Processing configuration: %s (ID: %s)", config.name, config.id)
                config = config.with_company(config.company_id).sudo()
                leads = config._get_leads_to_process()

                if not leads:
                    _logger.info("No matching leads found for configuration %s", config.name)
                    continue

                _logger.info("Found %d leads to process for configuration %s", len(leads), config.name)

                for lead in leads:
                    _logger.info("Processing lead %s (ID: %s)", lead.name, lead.id)
                    config._send_email_to_lead(lead)

                config.last_execution = fields.Datetime.now()
                self.env.cr.commit()
                _logger.info("Successfully processed configuration %s", config.name)

            except Exception as e:
                _logger.error("Error processing configuration %s: %s", config.name, str(e), exc_info=True)
                self.env.cr.rollback()
                config.message_post(
                    body=_("Error processing automatic emails: %s") % str(e)
                )

    def _get_leads_to_process(self, limit=None):
        """Get opportunities that should receive emails, based on exact days after stage entry"""
        self.ensure_one()

        # Get current time in company timezone
        company_tz = timezone(self.company_id.partner_id.tz or 'UTC')
        now_utc = fields.Datetime.now()
        now_tz = utc.localize(now_utc).astimezone(company_tz)

        # Calculate target date in company timezone (midnight X days ago)
        target_date_tz = (now_tz - timedelta(days=self.days_after)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Convert to UTC for database query
        target_date_utc = target_date_tz.astimezone(utc).replace(tzinfo=None)
        next_day_utc = (target_date_tz + timedelta(days=1)).astimezone(utc).replace(tzinfo=None)

        domain = [
            ('type', '=', 'opportunity'),
            ('stage_id', 'in', self.stage_ids.ids),
            ('stage_entry_date', '>=', target_date_utc),
            ('stage_entry_date', '<', next_day_utc),
            ('company_id', '=', self.company_id.id),
            ('active', '=', True),
            ('email_from', '!=', False),
            ('email_from', '!=', ''),
        ]

        if self.team_id:
            domain.append(('team_id', '=', self.team_id.id))
        if self.user_id:
            domain.append(('user_id', '=', self.user_id.id))
        if self.tag_ids:
            domain.append(('tag_ids', 'in', self.tag_ids.ids))
        if self.final:
            domain.append(('final_status', '=', self.final))

        return self.env['crm.lead'].search(domain, limit=limit)

    def _send_email_to_lead(self, lead):
        """Send automatic email to a lead based on the configuration"""
        self.ensure_one()


        email_body = f"""
        <p>Dear {lead.name or 'Customer'},</p>

        <p>{self.body_html}</p>

        <p>Best regards,<br/>
        {lead.user_id.name or 'The Sales Team'}<br/>
        {lead.company_id.name or ''}</p>
        Web: <a href="http://www.analytix.sa">www.analytix.sa</a></p>
            <br/>
            <div style="text-align: left; margin-bottom: 20px;">
                <img src="https://analytixtech.io/emailsign/analytix_logo_reveal.gif" alt="Analytix Logo" style="max-width: 200px;">
            </div>
             
            <p>___________________________________________</p>
        """


        email_from = self._get_sender_email(lead)


        email_values = {
            'subject': self.subject,
            'body_html': email_body,
            'email_from': email_from,
            'email_to': lead.email_from,
            'auto_delete': True,
            'attachment_ids': [(6, 0, self.attachment_ids.ids)] if self.attachment_ids else False,
        }

        # Add optional fields if they exist
        if self.reply_to:
            email_values['reply_to'] = self.reply_to
        if self.cc_emails:
            email_values['email_cc'] = self.cc_emails
        if self.attachment_ids:
            email_values['attachment_ids'] = [(6, 0, self.attachment_ids.ids)]

        # Create and send the email
        try:
            mail = self.env['mail.mail'].sudo().create(email_values)
            mail.send()

            # Create a message on the lead to track this automatic email
            lead.message_post(
                subject=self.subject,
                email_from=email_from,
                message_type='email',
                subtype_xmlid='crm_welcome_mail.mt_automatic_email',
            )

            _logger.info("Sent no-response email to lead %s", lead.name)
            return True

        except Exception as e:
            _logger.error("Failed to send no-response email: %s", str(e))
            return False

    def _get_sender_email(self, lead):
        """Determine the appropriate sender email address with fallbacks"""
        self.ensure_one()

        # Priority 1: Configuration's specified email
        if self.email_from:
            return self.email_from

        # Priority 2: Lead's assigned user email
        if lead.user_id and lead.user_id.email_formatted:
            return lead.user_id.email_formatted

        # Priority 3: Company email from lead's company
        if lead.company_id and lead.company_id.email_formatted:
            return lead.company_id.email_formatted

        # Priority 4: Current user's email
        if self.env.user.email_formatted:
            return self.env.user.email_formatted

        # Priority 5: Default company email
        company = self.company_id or self.env.company
        if company.email_formatted:
            return company.email_formatted

        # Final fallback
        _logger.warning("No valid sender email found for lead %s", lead.id)
        return "noreply@%s" % (lead.company_id.website or self.env['ir.config_parameter'].get_param('web.base.url',
                                                                                                    'yourcompany.com'))

    def action_test_configuration(self):
        leads = self._get_leads_to_process()
        _logger.info("Leads to process: %s", leads.mapped('name'))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Test Results"),
                'message': _("Found %d matching leads/opportunities") % len(leads),
                'sticky': False,
            }
        }


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    stage_entry_date = fields.Datetime(
        string='Stage Entry Date',
        help="When the lead/opportunity entered the current stage",
        store=True,
        copy=False
    )
    automatic_mail_count = fields.Integer(
        string='Auto Emails Sent',
        compute='_compute_automatic_mail_count',
        store=False,
        help="Number of automatic emails sent for this lead/opportunity"
    )

    @api.depends('message_ids')
    def _compute_automatic_mail_count(self):
        subtype_id = self.env.ref('crm_welcome_mail.mt_automatic_email').id
        for lead in self:
            lead.automatic_mail_count = len(lead.message_ids.filtered(
                lambda m: m.subtype_id.id == subtype_id and m.message_type == 'email'
            ))

    def write(self, vals):
        if 'stage_id' in vals:
            for lead in self:
                if vals['stage_id'] != lead.stage_id.id:
                    vals['stage_entry_date'] = fields.Datetime.now()
        return super(CRMLead, self).write(vals)


class MailMessage(models.Model):
    _inherit = 'mail.message'

    automatic_mail_config_id = fields.Many2one(
        'automatic.mail.config',
        string='Automatic Mail Configuration',
        help="Which automatic mail configuration sent this message",
        store=True
    )
    stage_id = fields.Many2one(
        'crm.stage',
        string='Stage',
        help="The stage the lead was in when this automatic email was sent",
        store=True
    )
