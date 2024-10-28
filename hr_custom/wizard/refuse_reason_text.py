from odoo import models, fields, api

class ApplicantRefuseReasonText(models.TransientModel):
    _inherit = 'applicant.get.refuse.reason'

    others = fields.Char(string="Other Reasons")

    @api.model
    def create(self, vals):
        """Override create to handle saving 'others_reason' to 'hr.applicant'."""
        record = super(ApplicantRefuseReasonText, self).create(vals)
        # Check if 'active_id' context key is provided to link with 'hr.applicant'
        applicant_id = self.env.context.get('active_id')
        if applicant_id and record.others:
            applicant = self.env['hr.applicant'].browse(applicant_id)
            if applicant.exists():
                applicant.write({'others_reason': record.others})
        return record
