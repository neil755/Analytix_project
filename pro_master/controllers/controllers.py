# -*- coding: utf-8 -*-
# from odoo import http


# class ProMaster(http.Controller):
#     @http.route('/pro_master/pro_master', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pro_master/pro_master/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pro_master.listing', {
#             'root': '/pro_master/pro_master',
#             'objects': http.request.env['pro_master.pro_master'].search([]),
#         })

#     @http.route('/pro_master/pro_master/objects/<model("pro_master.pro_master"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pro_master.object', {
#             'object': obj
#         })

