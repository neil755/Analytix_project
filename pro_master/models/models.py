from odoo import models, fields, api


class ProMasterLegal(models.Model):
    _name = 'pro.master.legal'

    name = fields.Char(string='Legal Structure')


class ProMasterOwnership(models.Model):
    _name = 'pro.master.ownership'

    name = fields.Char(string='Ownership Type')


class ProMasterContractStatus(models.Model):
    _name = 'pro.master.contract'

    name = fields.Char(string='GRO/PRO Contact Status')


class ProMasterDocumentStatus(models.Model):
    _name = 'pro.master.document'

    name = fields.Char(string='Document')


class ProMasterDocumentRenewalStatus(models.Model):
    _name = 'pro.master.document.status'

    name = fields.Char(string='Renewal Status')


class ProMasterEmployeeStatus(models.Model):
    _name = 'pro.master.employee.status'

    name = fields.Char(string='Employee Sponsorship Status')


class ProMasterResidentStatus(models.Model):
    _name = 'pro.master.resident.status'

    name = fields.Char(string='Resident ID  Status')


class ProMasterCompliance(models.Model):
    _name = 'pro.master.compliance'

    name = fields.Char(string='Compliance Name')


class ProMasterComplianceStatus(models.Model):
    _name = 'pro.master.compliance.status'

    name = fields.Char(string='Compliance Status')


class ProMasterFiling(models.Model):
    _name = 'pro.master.filing'

    name = fields.Char(string='Filing')


class ProMasterNotification(models.Model):
    _name = 'pro.master.notification'

    name = fields.Char(string='Notification')


class ProMasterWork(models.Model):
    _name = 'pro.master.work'

    name = fields.Char(string='Work Name')


class ProMasterWorkStatus(models.Model):
    _name = 'pro.master.work.status'

    name = fields.Char(string='Work Status')


class ProMaster(models.Model):
    _name = 'pro.master'
    _description = 'PRO Master File'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Many2one('res.partner', string='Customer/Company Name', tracking=True)
    serial_number = fields.Char(string='Client ID', readonly=True, copy=False)
    company_reg = fields.Char(string='Company Registration Trade Name', tracking=True)
    business_type = fields.Many2one('business.type', string='Business Type', tracking=True)
    business_activity = fields.Char(string='Business Activity', tracking=True)
    legal_structure = fields.Many2one('pro.master.legal', string='Legal Structure', tracking=True)
    ownership_type = fields.Many2one('pro.master.ownership', string='Ownership Type', tracking=True)
    vat_no = fields.Char(string='VAT Number', tracking=True)
    commercial_no = fields.Char(string='Commercial Registration Number', tracking=True)
    date_incorporation = fields.Date(string='Date of Incorporation', tracking=True)
    country_id = fields.Many2one('res.country', string='Country of Origin(for foreign investors)', tracking=True)
    shareholder_name = fields.Char(string='Shareholder Co Name (for foreign investors)', tracking=True)
    bs_code = fields.Char(string='BS Code', tracking=True)
    gro_pro_code = fields.Char(string='GRO/PRO Code', tracking=True)
    audit_code = fields.Char(string='Audit Code', tracking=True)
    ext_code = fields.Char(string='EXT Code', tracking=True)
    gro_pro_status = fields.Many2one('pro.master.contract', string='GRO/PRO Contact Status', tracking=True)

    primary_contact = fields.Char(string='Primary Contact Person (Full Name)', tracking=True)
    position = fields.Char(string='Position/Designation', tracking=True)
    phone = fields.Char(string='Phone Number', tracking=True)
    mobile = fields.Char(string='Mobile Number', tracking=True)
    whatsapp_no = fields.Char(string='WhatsApp Number', tracking=True)
    email = fields.Char(string='Email Address', tracking=True)
    address = fields.Char(string='Office Address (Street, City, Country, Postal Code)', tracking=True)
    mail_address = fields.Char(string='Mailing Address (if different from office)', tracking=True)
    website_name = fields.Char(string='Company Website URL', tracking=True)

    bank_name = fields.Char(string='Bank Name', tracking=True)
    bank_number = fields.Char(string='Bank Account Number', tracking=True)
    iban = fields.Char(string='IBAN', tracking=True)
    bank_branch = fields.Char(string='Bank Branch', tracking=True)
    currency = fields.Char(string='Currency (if relevant)', tracking=True)
    bank_type = fields.Char(string='Bank Account Type', tracking=True)

    preferred_language = fields.Char(string='Preferred Language', tracking=True)
    communication_preference = fields.Many2one('communication.channel', string='Communication Channel Preferences',
                                               tracking=True)
    contacts_note = fields.Char(string='Communication Preferences Notes', tracking=True)

    document = fields.Many2one('pro.master.document', string='Document (CR,MISA,etc)', tracking=True)
    document_no = fields.Char(string='Document Number', tracking=True)
    issuing_auth = fields.Char(string='Issuing Authority', tracking=True)
    issue_date = fields.Date(string='Issue Date', tracking=True)
    expiry_date = fields.Date(string='Expiry Date', tracking=True)
    renewal_status = fields.Many2one('pro.master.document.status')
    attachments_ids = fields.Many2many(
        'ir.attachment',
        'pro_master_attachment_rel',
        'master_id',
        'attachment_id',
        string='Attachments', tracking=True)
    company_note = fields.Char(string='Company Document Notes', tracking=True)

    employee_name = fields.Char(string='Employee Names', tracking=True)
    employee_designation = fields.Char(string='Employee Designation', tracking=True)
    nation_id = fields.Many2one('res.country', string='Nationality', tracking=True)
    employee_status = fields.Many2one('pro.master.employee.status', string='Employee Sponsorship Status', tracking=True)
    resident_status = fields.Many2one('pro.master.resident.status', string='Resident ID Status', tracking=True)
    contract_date = fields.Date(string='Work Visa / Contract Expiry Date', tracking=True)
    resident_no = fields.Char(string='Resident ID Number (for sponsored employees)', tracking=True)
    resident_date = fields.Date(string='Resident ID Expiry Date', tracking=True)
    reentry_date = fields.Date(string='Re-entry Visa Expiry Date', tracking=True)
    employee_attachment_ids = fields.Many2many(
        'ir.attachment',
        'pro_master_employee_attachment_rel',
        'master_id',
        'attachment_id',
        string='Employee Resident ID (Attachment)', tracking=True)
    employee_contract_ids = fields.Many2many(
        'ir.attachment',
        'pro_master_employee_contract_rel',
        'master_id',
        'attachment_id',
        string='Employee Contract (Attachment)', tracking=True)
    employee_passport_ids = fields.Many2many(
        'ir.attachment',
        'pro_master_employee_passport_rel',
        'master_id',
        'attachment_id',
        string='Employee Passport (Attachment)', tracking=True)
    employee_doc_ids = fields.Many2many(
        'ir.attachment',
        'pro_master_employee_doc_rel',
        'master_id',
        'attachment_id',
        string='Employee other Doc (Attachment)', tracking=True)

    compliance_name = fields.Many2one('pro.master.compliance', string='Compliance Name', tracking=True)
    compliance_status = fields.Many2one('pro.master.compliance.status', string='Compliance Status', tracking=True)
    filing_date = fields.Date(string='Filings Due Date', tracking=True)
    filing_status = fields.Many2one('pro.master.filing', string='Filings Status', tracking=True)
    notification_status = fields.Many2one('pro.master.notification', string='Notification Status', tracking=True)
    compliance_note = fields.Char(string='Compliance Note', tracking=True)

    portal_name = fields.Char(string='Portal Name', tracking=True)
    user_name = fields.Char(string='Username', tracking=True)
    password = fields.Char(string='Password', tracking=True)
    login_expiry_date = fields.Date(string='Login Expiry Date', tracking=True)

    work_name = fields.Many2one('pro.master.work', string='Work Name', tracking=True)
    work_detail = fields.Char(string='Work Detail', tracking=True)
    work_status = fields.Many2one('pro.master.work.status', string='Work Status', tracking=True)
    completed_date = fields.Date(string='Completed Date', tracking=True)
    work_note = fields.Char(string='Work Note', tracking=True)

    @api.model
    def create(self, vals):
        if not vals.get('serial_number') or vals.get('serial_number') == '/':
            vals['serial_number'] = self.env['ir.sequence'].next_by_code('pro_master.serial') or '/'
        return super(ProMaster, self).create(vals)
