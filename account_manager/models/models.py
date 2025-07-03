# -*- coding: utf-8 -*-

from odoo import models, fields, api


class UserEmployee(models.Model):
    _inherit = 'res.users'

    is_account_manager = fields.Boolean(
        string='Is Account Manager',
        help='Check this box if the employee is an Account Manager',
        default=False
    )
