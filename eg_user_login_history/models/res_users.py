from odoo import fields, models, api
from datetime import datetime
from odoo.http import request


class ResUsers(models.Model):
    _inherit = "res.users"

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        res = super(ResUsers, cls)._login(db, login, password, user_agent_env)
        user_id = request.env["res.users"].sudo().search([("login", "=", login)]) if login else request.env["res.users"]
        request.env["user.attendance"].create({
            "attendance_id": user_id.id,
            "db_name": db,
            "user_agent": request.httprequest.cookies,
            "login_time": datetime.now()
        })
        return res
