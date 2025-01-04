from odoo import models, fields, api
from datetime import timedelta, date
import logging

_logger = logging.getLogger(__name__)


class hr_custom(models.Model):
    _inherit = 'hr.applicant'

    appli_status = fields.Selection([('ca', 'CA'),
                                     ('rnr', 'RNR'), ('cb', 'CB'), ('sw', 'SW '), ('nr', 'NR'), ('fu', 'FU')],
                                    string="Status", tracking=True)
    apply_date = fields.Date(string='Applied Date', default=fields.Date.today, tracking=True)
    location_cand = fields.Char(string="Location of Applicant", tracking=True)
    location_add = fields.Char(string="Location", tracking=True)

    qualification = fields.Char(string="Qualification", tracking=True)
    time_join = fields.Char(string="Time to Join", tracking=True)
    work_exp = fields.Char(string="Relevant Experience ", tracking=True)
    total_exp = fields.Char(string="Total Experience ", tracking=True)
    change_reason = fields.Char(string="Reason for change", tracking=True)
    com_skill = fields.Selection(
        [('0', 'Normal'), ('1', 'Below Average'), ('2', 'Intermediate'), ('3', 'Average'), ('4', 'Good'),
         ('5', 'Excellent')],
        default='0', string="Communication Skill", tracking=True)
    eng_skill = fields.Selection(
        [('0', 'Normal'), ('1', 'Below Average'), ('2', 'Intermediate'), ('3', 'Average'), ('4', 'Good'),
         ('5', 'Excellent')],
        default='0', string="English", tracking=True)
    exl_skill = fields.Selection(
        [('0', 'Normal'), ('1', 'Below Average'), ('2', 'Intermediate'), ('3', 'Average'), ('4', 'Good'),
         ('5', 'Excellent')],
        default='0', string="Excel Skill", tracking=True)
    tec_skill = fields.Selection(
        [('0', 'Normal'), ('1', 'Below Average'), ('2', 'Intermediate'), ('3', 'Average'), ('4', 'Good'),
         ('5', 'Excellent')],
        default='0', string="Basic Technical Skill", tracking=True)

    personal_email = fields.Char(string="Personal Email ID", tracking=True)
    behaviour_analysis = fields.Char(string="Behavioral Analysis", tracking=True)
    company_procedure = fields.Char(string="Company Procedure", tracking=True)
    hr_feedback = fields.Char(string="HR Round Feedback", tracking=True)
    mgr_feedback = fields.Char(string="Managers Round Feedback", tracking=True)
    email_confirm = fields.Char(string="Email Confirmation Status", tracking=True)
    offer_accept = fields.Char(string="Offer Acceptance Status", tracking=True)
    remark_msg = fields.Char(string="Remarks", tracking=True)
    others_reason = fields.Char(string="Other Refuse Reason", tracking=True)


class hr_job_custom(models.Model):
    _inherit = 'hr.job'

    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    deadline_date = fields.Date(string='Deadline', tracking=True)
    is_deadline_passed = fields.Boolean(string='Is Deadline Passed', compute='_compute_is_deadline_passed', store=True)
    days_to_deadline = fields.Integer(string='Days to Deadline', compute='_compute_days_to_deadline')

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date:

            self.deadline_date = self.start_date + timedelta(days=30)
        else:
            self.deadline_date = False

    @api.depends('deadline_date')
    def _compute_is_deadline_passed(self):
        current_date = fields.Date.context_today(self)
        for record in self:
            record.is_deadline_passed = bool(record.deadline_date and record.deadline_date < current_date)

    @api.depends('deadline_date')
    def _compute_days_to_deadline(self):
        current_date = fields.Date.context_today(self)
        for record in self:
            if record.deadline_date:
                delta = (record.deadline_date - current_date).days
                record.days_to_deadline = delta if delta >= 0 else 0
                _logger.info(f"Days to Deadline for {record.name}: {record.days_to_deadline}")
            else:
                record.days_to_deadline = 0
                _logger.info(f"No deadline set for {record.name}")

