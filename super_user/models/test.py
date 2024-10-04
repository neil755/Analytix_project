# # my_module/views/lead_view.py
# from odoo import api, fields, models
# from odoo.tools import etree  # <--- Corrected import
#
# class LeadView(models.Model):
#     _inherit = 'crm.lead'
#
#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         result = super(LeadView, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         if view_type == 'form':
#             doc = etree.XML(result['arch'])
#             for node in doc.xpath("//button[@name='convert_opportunity']"):
#                 node.set('invisible', '1')
#             result['arch'] = etree.tostring(doc, encoding='unicode')
#         return result