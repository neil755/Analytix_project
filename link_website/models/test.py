# import xmlrpc.client
#
#
# url = 'http://localhost:6869'
# db = 'Test'
# username = 'admin'
# password = 'admin'
#
# common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
# print(common.version())
# uid = common.authenticate(db, username, password, {})
# print(uid)
#
# models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
# print(models.execute_kw(db, uid, password, 'res.partner', 'check_access_rights', ['read'], {'raise_exception': False}))
#
# print(models.execute_kw(db, uid, password, 'res.partner', 'search', [[['is_company', '=', True]]]))



# def Customers():
#     def create(self):
#         model_name = 'crm.lead'
#         vals = {
#             'contact_name': "Name",
#             'email_from': "Email",
#             'phone': "Phone Number",
#             'description': "Comment",
#         }
#         new_id = models.execute_kw(db, uid, password, model_name, 'create', [vals])
#         return new_id
