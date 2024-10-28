from odoo import models, fields, api


class hr_custom(models.Model):
    _inherit = 'hr.applicant'

    appli_status = fields.Selection([('ca', 'CA'),
                                     ('rnr', 'RNR'), ('cb', 'CB'), ('sw', 'SW '), ('nr', 'NR'), ('fu', 'FU')],
                                    string="Status", tracking=True)
    apply_date = fields.Date(string='Applied Date', default=fields.Date.today)
    location_add = fields.Char(string="Location")

    qualification = fields.Char(string="Qualification")
    time_join = fields.Char(string="Time to Join")
    work_exp = fields.Char(string="Relevant Experience ")
    total_exp = fields.Char(string="Total Experience ")
    change_reason = fields.Char(string="Reason for change")
    com_skill = fields.Selection(
        [('0', 'Normal'), ('1', 'Below Average'), ('2', 'Intermediate'), ('3', 'Average'), ('4', 'Good'),
         ('5', 'Excellent')],
        default='0', string="Communication Skill")
    eng_skill = fields.Selection(
        [('0', 'Normal'), ('1', 'Below Average'), ('2', 'Intermediate'), ('3', 'Average'), ('4', 'Good'),
         ('5', 'Excellent')],
        default='0', string="English")
    exl_skill = fields.Selection(
        [('0', 'Normal'), ('1', 'Below Average'), ('2', 'Intermediate'), ('3', 'Average'), ('4', 'Good'),
         ('5', 'Excellent')],
        default='0', string="Excel Skill")
    tec_skill = fields.Selection(
        [('0', 'Normal'), ('1', 'Below Average'), ('2', 'Intermediate'), ('3', 'Average'), ('4', 'Good'),
         ('5', 'Excellent')],
        default='0', string="Basic Technical Skill")

    personal_email = fields.Char(string="Personal Email ID")
    behaviour_analysis = fields.Char(string="Behavioral Analysis")
    company_procedure = fields.Char(string="Company Procedure")
    hr_feedback = fields.Char(string="HR Round Feedback")
    mgr_feedback = fields.Char(string="Managers Round Feedback")
    email_confirm = fields.Char(string="Email Confirmation Status")
    offer_accept = fields.Char(string="Offer Acceptance Status")
    remark_msg = fields.Char(string="Remarks")
    others_reason = fields.Char(string="Other Refuse Reason")


