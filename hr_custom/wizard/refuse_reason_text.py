from odoo import models, fields, api


class ApplicantRefuseReasonText(models.TransientModel):
    _inherit = 'applicant.get.refuse.reason'

    others = fields.Char(string="Other Reasons", tracking=True)

    @api.model
    def create(self, vals):

        record = super(ApplicantRefuseReasonText, self).create(vals)

        applicant_id = self.env.context.get('active_id')
        if applicant_id and record.others:
            applicant = self.env['hr.applicant'].browse(applicant_id)
            if applicant.exists():
                applicant.write({'others_reason': record.others})
        return record
