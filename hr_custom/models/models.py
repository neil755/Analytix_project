from odoo import models, fields


class hr_custom(models.Model):
    _inherit = 'hr.applicant'

    appli_status = fields.Selection([('ca', 'CA'),
                                     ('rnr', 'RNR'), ('cb', 'CB'), ('sw', 'SW '), ('nr', 'NR'), ('fu', 'FU')],
                                    string="Status", tracking=True)

    qualification = fields.Char(string="Qualification")
    time_join = fields.Char(string="Time to Join")
    work_exp = fields.Char(string="Work Experience ")
    change_reason = fields.Char(string="Reason for change")
    com_skill = fields.Selection(
        [('0', 'Normal'), ('1', 'Below Average'), ('2', 'Average'), ('3', 'Medium'), ('4', 'Good'), ('5', 'Excellent')],
        default='0', string="Communication Skill")
    eng_skill = fields.Selection(
        [('0', 'Normal'), ('1', 'Below Average'), ('2', 'Average'), ('3', 'Medium'), ('4', 'Good'), ('5', 'Excellent')],
        default='0', string="English")
    exl_skill = fields.Selection(
        [('0', 'Normal'), ('1', 'Below Average'), ('2', 'Average'), ('3', 'Medium'), ('4', 'Good'), ('5', 'Excellent')],
        default='0', string="Excel Skill")
    tec_skill = fields.Selection(
        [('0', 'Normal'), ('1', 'Below Average'), ('2', 'Average'), ('3', 'Medium'), ('4', 'Good'), ('5', 'Excellent')],
        default='0', string="Basic Technical Skill")
    beh_analysis = fields.Selection(
        [('0', 'Too Questioning'), ('1', 'Job Inconsistency'), ('2', 'Attitude'), ('3', 'Dishonest'),
         ('4', 'Highly Positive'), ('5', 'Neutral'), ('6', 'Negative'), ('7', 'Highly Negative')],
        string="Behavioral Analysis")
    comp_procedure = fields.Selection(
        [('0', 'Agree'), ('1', 'Partially Agree'), ('2', 'Disagree'), ('3', 'Disagree (Certificate)'),
         ('4', 'Disagree (Notice Period)'), ('5', 'Disagree (Probation Period)')], string="Company Procedure")
    hr_feedback = fields.Char(string="HR Round Feedback")
    mgr_feedback = fields.Char(string="Managers Round Feedback")
    email_confirm = fields.Char(string="Email Confirmation Status")
    offer_accept = fields.Char(string="Offer Acceptance Status")
    remark_msg = fields.Char(string="Remarks")
