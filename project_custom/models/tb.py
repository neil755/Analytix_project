from odoo import models, fields, api


class project_tb_custom(models.Model):
    _name = 'tb.custom'
    _description = 'TB with Adj'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'particulars'

    particulars = fields.Char(string='Particulars', tracking=True)
    op_balance = fields.Float(string='Opening Balance', tracking=True)
    dr_amount = fields.Float(string='DR Amount', tracking=True)
    cr_amount = fields.Float(string='CR Amount', tracking=True)
    close_balance = fields.Float(string='Closing Balance')
    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )
class ProjectTBCustom(models.Model):
    _inherit = 'project.project'

    def action_view_tb_custom(self):

        return {
            'name': 'TB',
            'type': 'ir.actions.act_window',
            'res_model': 'tb.custom',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'default_company_id': self.company_id.id,
            },
        }

