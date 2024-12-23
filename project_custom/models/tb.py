# from odoo import models, fields, api
#
#
# class project_tb_custom(models.Model):
#     _name = 'tb.custom'
#     _description = 'TB with Adj'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _rec_name = 'particulars'
#
#     particulars = fields.Char(string='Particulars', tracking=True)
#     op_balance = fields.Float(string='Opening Balance', tracking=True)
#     dr_amount = fields.Float(string='DR Amount', tracking=True)
#     cr_amount = fields.Float(string='CR Amount', tracking=True)
#     close_balance = fields.Float(string='Closing Balance')
