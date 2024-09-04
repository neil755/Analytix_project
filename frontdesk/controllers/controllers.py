# -*- coding: utf-8 -*-
# from odoo import http


# class Frontdesk(http.Controller):
#     @http.route('/frontdesk/frontdesk', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/frontdesk/frontdesk/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('frontdesk.listing', {
#             'root': '/frontdesk/frontdesk',
#             'objects': http.request.env['frontdesk.frontdesk'].search([]),
#         })

#     @http.route('/frontdesk/frontdesk/objects/<model("frontdesk.frontdesk"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('frontdesk.object', {
#             'object': obj
#         })

