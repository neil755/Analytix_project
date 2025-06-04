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
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Mail Template',
        domain="[('model_id.model', '=', 'crm.lead')]",
        required=True
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
        """Send email to lead with proper email addressing"""
        self.ensure_one()
        try:
            if not lead.email_from:
                _logger.warning("Lead %s (ID: %s) has no email address", lead.name, lead.id)
                return False

            # Verify mail server is configured
            if not self.env['ir.mail_server'].search_count([]):
                _logger.error("No outgoing mail servers configured!")
                return False

            # Determine the sender
            email_from = lead.user_id.email_formatted if (
                    lead.user_id and lead.user_id.email_formatted) else self.company_id.email_formatted
            if not email_from:
                _logger.error("No valid sender email address found for lead %s", lead.id)
                return False

            # Prepare email values
            email_values = {
                'email_to': lead.email_from,
                'email_from': email_from,
                'author_id': lead.user_id.partner_id.id if lead.user_id else self.env.user.partner_id.id,
                'auto_delete': False,
            }

            # Send with template
            self.mail_template_id.with_context(
                default_email_from=email_from,
                default_author_id=email_values['author_id'],
            ).send_mail(
                lead.id,
                force_send=True,
                email_values=email_values
            )

            # Prepare message values
            message_vals = {
                'body': _("Automatic email sent: %s") % self.mail_template_id.subject,
                'subject': self.mail_template_id.subject,
                'subtype_id': self.env.ref('crm_welcome_mail.mt_automatic_email').id,
                'email_from': email_from,
                'author_id': email_values['author_id'],
                'message_type': 'email',
            }

            # Create the message first
            message = lead.message_post(**message_vals)

            # Then write the additional fields
            if message:
                message.write({
                    'stage_id': lead.stage_id.id,
                    'automatic_mail_config_id': self.id,
                })

            _logger.info("Successfully sent email to %s", lead.email_from)
            return True

        except Exception as e:
            _logger.error("Failed to send email to lead %s (ID: %s): %s\nTraceback: %s",
                          lead.name, lead.id, str(e), traceback.format_exc())
            lead.message_post(
                body=_("Failed to send automatic email: %s") % str(e),
                subtype_id=self.env.ref('mail.mt_note').id
            )
            return False
        except Exception as e:
            _logger.error("Failed to send email to lead %s (ID: %s): %s\nTraceback: %s",
                          lead.name, lead.id, str(e), traceback.format_exc())
            lead.message_post(
                body=_("Failed to send automatic email: %s") % str(e),
                subtype_id=self.env.ref('mail.mt_note').id
            )
            return False

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
        help="Which automatic mail configuration sent this message"
    )
    stage_id = fields.Many2one(
        'crm.stage',
        string='Stage',
        help="The stage the lead was in when this automatic email was sent"
    )
