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
    close_balance = fields.Float(string='Closing Balance', compute='_compute_close_balance', store=True, tracking=True)
    adj_dr_amount = fields.Float(string='Adjustmemt Entries - DR Amount', tracking=True)
    adj_cr_amount = fields.Float(string='Adjustmemt Entries - CR Amount', tracking=True)
    final_balance = fields.Float(string='Final Balance', compute='_compute_final_balance', store=True, tracking=True)
    adj_remarks = fields.Char(string='Remarks', tracking=True)

    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    @api.depends('op_balance', 'dr_amount', 'cr_amount')
    def _compute_close_balance(self):
        for record in self:
            record.close_balance = record.op_balance + record.dr_amount - record.cr_amount

    @api.depends('close_balance', 'adj_dr_amount', 'adj_cr_amount')
    def _compute_final_balance(self):
        for record in self:
            record.final_balance = record.close_balance + record.adj_dr_amount - record.adj_cr_amount


class ProjectTBCustom(models.Model):
    _inherit = 'project.project'

    def action_view_tb_custom(self):
        return {
            'name': 'TB with Adj ',
            'type': 'ir.actions.act_window',
            'res_model': 'tb.custom',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'default_company_id': self.company_id.id,
            },
        }
