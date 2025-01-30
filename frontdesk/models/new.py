# -*- coding: utf-8 -*-
#
# from odoo import models, fields
#
#
# class SimilarFields(models.Model):
#     _name = 'similar.fields'
#     _description = 'Similar Fields'
#
#     field1 = fields.Char(string='Field 1')
#     field2 = fields.Char(string='Field 2')
#     similarity = fields.Float(string='Similarity', compute='_compute_similarity')
#
#     def _compute_similarity(self):
#         # Implement your similarity calculation logic here
#         # For example, you can use the Levenshtein distance algorithm
#         for record in self:
#             record.similarity = self._calculate_similarity(record.field1, record.field2)
#
#     def _calculate_similarity(self, field1, field2):
#         # Implement your similarity calculation logic here
#         # For example, you can use the Levenshtein distance algorithm
#         distance = self._levenshtein_distance(field1, field2)
#         return 1 - (distance / max(len(field1), len(field2)))
#
#     def _levenshtein_distance(self, s1, s2):
#         if len(s1) < len(s2):
#             return self._levenshtein_distance(s2, s1)
#
#         if len(s2) == 0:
#             return len(s1)
#
#         previous_row = range(len(s2) + 1)
#         for i, c1 in enumerate(s1):
#             current_row = [i + 1]
#             for j, c2 in enumerate(s2):
#                 insertions = previous_row[j + 1] + 1
#                 deletions = current_row[j] + 1
#                 substitutions = previous_row[j] + (c1 != c2)
#                 current_row.append(min(insertions, deletions, substitutions))
#             previous_row = current_row
#
#         return previous_row[-1]
#         <?xml version="1.0" encoding="utf-8"?>
# <odoo>
#     <data>
#         <record id="similar_fields_form" model="ir.ui.view">
#             <field name="name">Similar Fields Form</field>
#             <field name="model">similar.fields</field>
#             <field name="arch" type="xml">
#                 <form>
#                     <group>
#                         <field name="field1"/>
#                         <field name="field2"/>
#                         <field name="similarity"/>
#                     </group>
#                 </form>
#             </field>
#         </record>
#
#         <record id="similar_fields_tree" model="ir.ui.view">
#             <field name="name">Similar Fields Tree</field>
#             <field name="model">similar.fields</field>
#             <field name="arch" type="xml">
#                 <tree>
#                     <field name="field1"/>
#                     <field name="field2"/>
#                     <field name="similarity"/>
#                 </tree>
#             </field>
#         </record>
#
#         <record id="similar_fields_action" model="ir.actions.act_window">
#             <field name="name">Similar Fields</field>
#             <field name="res_model">similar.fields</field>
#             <field name="view_mode">tree,form</field>
#         </record>
#
#         <menuitem id="similar_fields_menu" name="Similar Fields" parent="base.menu_root"/>
#         <menuitem id="similar_fields_submenu" name="Similar Fields" parent="similar_fields_menu" action="similar_fields_action"/>
#     </data>
# </odoo>
#
#
#


