# -*- coding: utf-8 -*-
# from odoo import http


# class ProjectCustom(http.Controller):
#     @http.route('/project_custom/project_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_custom/project_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_custom.listing', {
#             'root': '/project_custom/project_custom',
#             'objects': http.request.env['project_custom.project_custom'].search([]),
#         })

#     @http.route('/project_custom/project_custom/objects/<model("project_custom.project_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_custom.object', {
#             'object': obj
#         })

