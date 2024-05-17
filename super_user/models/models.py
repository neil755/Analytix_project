from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, values):
        user = self.env.user
        if user.email == 'neil@analytix.org':
            # Provide default values for mandatory fields if not provided
            for field_name, field in self._fields.items():
                if field.required and field_name not in values:
                    # Provide default values based on field type
                    if field.type == 'char':
                        values[field_name] = ''
                    elif field.type == 'integer':
                        values[field_name] = 0
                    elif field.type == 'float':
                        values[field_name] = 0.0
                    elif field.type == 'boolean':
                        values[field_name] = False
                    elif field.type == 'many2one':
                        values[field_name] = False
                    elif field.type in ['date', 'datetime']:
                        values[field_name] = fields.Datetime.now()
                    elif field.type == 'selection' and field.selection:
                        values[field_name] = field.selection[0][0]
                    else:
                        values[field_name] = False  # Default fallback for other types
        else:
            # Check mandatory fields for other users
            for field_name, field in self._fields.items():
                if field.required and field_name not in values:
                    raise ValueError(f"Field '{field_name}' is mandatory and must be set.")

        return super(CrmLead, self).create(values)

# from odoo import models, api, SUPERUSER_ID, _
#
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class CustomLead(models.Model):
#     _inherit = 'crm.lead'
#
#     @api.model
#     def create(self, vals):
#         user = self.env.user
#         _logger.info("User: %s", user.login)
#
#         if user.login == 'neil@analytix.org':
#             _logger.info("Creating lead for specified user.")
#             lead = self.sudo(SUPERUSER_ID).create(vals)
#             return lead
#         else:
#             _logger.info("Creating lead for other users.")
#             return super(CustomLead, self).create(vals)

# from odoo import models, api
#
#
# class CustomLead(models.Model):
#     _inherit = 'crm.lead'
#
#     @api.model
#     def create(self, vals):
#         # Get the user object
#         user = self.env.user
#
#         # Check if the user is the specific user by email
#         if user.login == 'neil@analytix.org':
#             # Bypass the required fields
#             # Here we make sure we bypass the constraints for mandatory fields
#             # by temporarily disabling the constraints
#
#             # Get the original constraints
#             mandatory_fields = self._fields.get('required', {})
#
#             # Temporarily disable the required constraint for each field
#             for field_name, field in mandatory_fields.items():
#                 field.required = False
#
#             # Create the record
#             lead = super(CustomLead, self).create(vals)
#
#             # Restore the original constraints
#             for field_name, field in mandatory_fields.items():
#                 field.required = True
#
#             return lead
#         else:
#             # Normal creation process for other users
#             return super(CustomLead, self).create(vals)

# from odoo import models, fields, api, SUPERUSER_ID
#
#
# class CrmLead(models.Model):
#     _inherit = 'crm.lead'
#
#     @api.model
#     def create(self, vals):
#         if self.env.uid == SUPERUSER_ID or self.env.user.has_group('base.group_system'):
#             # Bypass mandatory fields check for superuser or users in Administration/Settings group
#             return super(CrmLead, self.with_context(ignore_mandatory=True)).create(vals)
#         else:
#             return super(CrmLead, self).create(vals)
#
#     # def write(self, vals):
#     #     if self.env.uid == SUPERUSER_ID or self.env.user.has_group('base.group_system'):
#     #         # Bypass mandatory fields check for superuser or users in Administration/Settings group
#     #         return super(CrmLead, self.with_context(ignore_mandatory=True)).write(vals)
#     #     else:
#     #         return super(CrmLead, self).write(vals)
#
#     @api.model
#     def _check_mandatory_fields(self, fields):
#         if self.env.context.get('ignore_mandatory'):
#             return
#         return super(CrmLead, self)._check_mandatory_fields(fields)
