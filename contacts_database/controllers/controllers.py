# -*- coding: utf-8 -*-
# from odoo import http


# class ContactsDatabase(http.Controller):
#     @http.route('/contacts_database/contacts_database', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contacts_database/contacts_database/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('contacts_database.listing', {
#             'root': '/contacts_database/contacts_database',
#             'objects': http.request.env['contacts_database.contacts_database'].search([]),
#         })

#     @http.route('/contacts_database/contacts_database/objects/<model("contacts_database.contacts_database"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contacts_database.object', {
#             'object': obj
#         })

