from odoo import models, fields, api

class ResPartnerInherited(models.Model):
    _inherit = 'res.partner'

    reference = fields.Char(string="Ref Number")
    date = fields.Date(string="Date")
    fax = fields.Char(string="Fax")
    tax_registration_number = fields.Char(string="Tax Registration Number")
    trade_license_number = fields.Char(string="Trade License Number")
    date_of_establishment = fields.Date(string="Date of Establishment")
    sponsor = fields.Char(string="Name of the local sponsor")
    proprietor = fields.Char(string="Proprietor/Partner Full Name")
    nationality = fields.Char(string="Nationality")
    emirates_id = fields.Char(string="Emirates ID")
    #Account Information
    name_of_the_bank = fields.Char(string="Name of The Bank")
    branch = fields.Char(string="Branch")
    account_no = fields.Integer(string="Account no")
    iban_no = fields.Char(string="IBAN No")
    #Authorised Signatory on behalf of the Company
    name1 = fields.Char(string="Name")
    signature_stamp1 = fields.Binary(string="Signature & Stamp")
    name2 = fields.Char(string="Name")
    signature_stamp2 = fields.Binary(string="Signature & Stamp")
    name3 = fields.Char(string="Name")
    signature_stamp3 = fields.Binary(string="Signature & Stamp")

    #Credit Facility
    credit_limit = fields.Float(string="Credit Limit in AED")
    post_restriction_on_credit = fields.Boolean(string="Post Restriction On Credit", default=False)

    #Terms & Conditions
    #Declaration
    signature_of_local_owner = fields.Binary(string="Signature Of Local Manager")
    signature_of_local_owner_date = fields.Date(string="Date")
    signature_of_local_manager = fields.Binary(string="Signatur Of Local Manager")
    signature_of_local_manager_date = fields.Date(string="Date")
    company_stamp = fields.Binary(string="Company Stamp")
    #for office use only
    # credit_limit = fields.Float(string="Credit Limit in AED")
    credit_period = fields.Char(string="Credit Period")
    days = fields.Integer(string="Days")
    sales_department = fields.Char(string="Sales Department")
    sales_manager = fields.Char(string="Sales Manager")
    finance_dept = fields.Char(string="Finance Dept")
    status = fields.Selection([('draft', 'Draft'),
                              ('o_approve', 'Operational Approved'),
                              ('f_approve', 'Finance Approved')], string='Customer Validation Status', readonly=True, default='draft')
    customer_validate = fields.Boolean(string="Verified", readonly=True)
    is_doctor = fields.Boolean(string="Is A Doctor")
    is_a_vendor = fields.Boolean(string="Is A Vendor")
    is_a_customer = fields.Boolean(string="Is A Pharmacy")
    is_a_salesperson = fields.Boolean(string="Is A Salesperson")
    is_a_hospital = fields.Boolean(string="Is A Hospital")
    is_a_clinic = fields.Boolean(string="Is A Clinic")


    # tag&customer_territory
    customer_territory = fields.Char(string="Customer Territory")
    vat_id = fields.Char(string="VAT ID")
    crm_lead_count = fields.Integer(string="Lead count", default=0)
    salesperson_visit_count = fields.Integer(string="Salesperson visit count",
                                             compute="compute_salesperson_visit_count")
    #visit
    visit_ids = fields.One2many('res.partner.visit','partner_id',string="Visit IDS")
    partner_id = fields.Many2one('res.partner', string="Partner")
    pharmacy_id = fields.Many2one('res.partner', string="Pharmacy")
    pharmacy_ids = fields.Many2many('res.partner', string="Pharmacy", relation="partner_pharmacy_rel", column1="partner_id", column2="pharmacy_id")
    doctor_ids = fields.Many2many('res.partner', string="Doctor", relation="doctor_pharmacy_rel",
                                    column1="partner_id", column2="pharmacy_id")
    not_write = fields.Boolean(string="Not write", default=False)

    def compute_salesperson_visit_count(self):
        for rec in self:
            user_id = self.env['res.users'].search([('partner_id', '=', rec.id)], limit=1)
            if user_id:
                visit_count = self.env['lead.details'].search_count([('salesperson', '=', user_id.id)])
                if visit_count:
                    rec.salesperson_visit_count = visit_count
                else:
                    rec.salesperson_visit_count = 0
            else:
                rec.salesperson_visit_count = 0

    def visit(self):
        for rec in self:
            # lead_details_obj = self.env['lead.details']
            # second_stage = self.env['crm.stage'].search([('sequence', '=', 2)], limit=1)
            # leads = self.env['crm.lead'].search([('stage_id', '=', second_stage.id), ('partner_id', '=', rec.id)])
            # if leads:
            #     for lead in leads:
            #         existing_lead_details = lead_details_obj.search([
            #             ('lead_name', '=', lead.id),
            #             ('customer', '=', rec.id),
            #         ], limit=1)
            #
            #         if not existing_lead_details:
            #             # Create data in the 'lead.details' model
            #             lead_details_vals = {
            #                 'lead_name': lead.id,
            #                 'salesperson': lead.user_id.id,
            #                 'date': lead.create_date,
            #                 'customer': lead.partner_id.id,
            #                 'sales_team': lead.team_id.id,
            #                 # 'sale_order_count': lead.sale_order_count,  # Adjust as needed
            #             }
            #
            #             lead_details_obj.create(lead_details_vals)

            action = self.env.ref('ddl_nc_customer_credit_form.action_lead_details').read()[0]
            # if self.is_a_salesperson:
            #     action['domain'] = [('customer', '=', rec.id)]

            action['domain'] = [('customer', '=', rec.id)]
            return action

    def visit_salesperson(self):
        for rec in self:
            user_id = self.env['res.users'].search([('partner_id', '=', rec.id)], limit=1)
            action = self.env.ref('ddl_nc_customer_credit_form.action_lead_details').read()[0]
            action['domain'] = [('salesperson', '=', user_id.id)]
            return action

    def salesperson_target(self):
        for rec in self:
            user_id = self.env['res.users'].search([('partner_id', '=', rec.id)], limit=1)
            action = self.env.ref('ddl_nc_customer_credit_form.action_salesperson_target').read()[0]
            action['domain'] = [('salesperson', '=', user_id.id)]
            return action


    @api.model
    def create(self, vals):
        # Check if customer_territory exists in res.partner.category

        category_name = vals.get('customer_territory')
        category = self.env['res.partner.category'].search([('name', '=', category_name)], limit=1)

        # If not, create a new category
        if not category and category_name:
            category = self.env['res.partner.category'].create({'name': category_name})

        # Update category_id in res.partner
        if category_name:
            vals['category_id'] = [(4, category.id, None)]

        if vals.get('is_doctor'):
            vals['customer_validate'] = True
            vals['status'] = 'f_approve'
        if vals.get('is_a_customer'):
            vals['customer_validate'] = True
            vals['status'] = 'f_approve'
        if vals.get('is_a_vendor'):
            vals['customer_validate'] = True
            vals['status'] = 'f_approve'

        # Call the super method to complete the create process
        return super(ResPartnerInherited, self).create(vals)

    def write(self, vals):
        # Check if customer_territory is being updated
        if 'customer_territory' in vals:
            # Check if the new category exists in res.partner.category
            category_name = vals['customer_territory']
            category = self.env['res.partner.category'].search([('name', '=', category_name)], limit=1)

            # If not, create a new category
            if not category:
                category = self.env['res.partner.category'].create({'name': category_name})

            # Update category_id in res.partner
            vals['category_id'] = [(4, category.id, None)]

            if category_name:
                vals['category_id'] = [(4, category.id, None)]

        if 'is_doctor' in vals and vals['is_doctor']:
            vals['customer_validate'] = True
            vals['status'] = 'f_approve'
            vals['is_company'] = False

        if 'is_a_customer' in vals and vals['is_a_customer']:
            vals['customer_validate'] = True
            vals['status'] = 'f_approve'
            vals['is_company'] = True

        if 'is_a_vendor' in vals and vals['is_a_vendor']:
            vals['customer_validate'] = True
            vals['status'] = 'f_approve'
            vals['is_company'] = True

        if 'parent_id' in vals and vals['parent_id']:
            vals['is_doctor'] = True

        if 'is_a_salesperson' in vals and vals['is_a_salesperson']:
            vals['is_company'] = False

        if 'is_a_hospital' in vals and vals['is_a_hospital']:
            vals['is_company'] = True

        if 'is_a_clinic' in vals and vals['is_a_clinic']:
            vals['is_company'] = True

        # Call the super method to complete the write process
        return super(ResPartnerInherited, self).write(vals)

    def sold_items(self):
        # partner_id = self.id
        # print("id", partner_id)
        # self.env.cr.execute("""
        #             SELECT
        #                 move.name AS move_name,
        #                 move.invoice_origin AS move_invoice_origin,
        #                 move.invoice_date AS move_invoice_date,
        #                 move.state AS move_state,
        #                 move.partner_id AS move_partner_id,
        #                 line.id AS line_id,
        #                 line.name AS line_name,
        #                 line.product_id AS line_product_id,
        #                 line.quantity AS quantity,
        #                 line.price_unit AS price_unit
        #
        #             FROM account_move move
        #             JOIN account_move_line line ON move.id = line.move_id
        #             WHERE move.state = 'posted' AND move.partner_id = %s
        #         """, (partner_id,))
        #
        # result = self.env.cr.fetchall()
        # print(result)
        #
        # for row in result:
        #     move_name, move_invoice_origin, move_invoice_date, move_state, move_partner_id, line_id, line_name, line_product_id, quantity, price_unit = row
        #     if line_product_id:
        #         sold_item = self.env['sold.item'].search([
        #             ('invoice_no', '=', move_name),
        #             ('invoice_line_id', '=', line_id),
        #             ('customer', '=', move_partner_id),
        #         ], limit=1)
        #
        #         if sold_item:
        #             # Update existing record
        #             sold_item.write({
        #                 'quantity': quantity,
        #                 'price_unit': price_unit,
        #             })
        #         else:
        #             # Create new record
        #             self.env['sold.item'].create({
        #                 'customer': move_partner_id,  # Assuming move_partner_id is the customer ID
        #                 'invoice_no': move_name,
        #                 'invoice_origin': move_invoice_origin,
        #                 'invoice_line_id': line_id,
        #                 'invoice_date': move_invoice_date,
        #                 'product_id': line_product_id,  # You need to replace None with the actual product ID
        #                 'quantity': quantity,
        #                 'price_unit': price_unit,
        #                 'recommended_by': None  # You need to replace None with the actual recommended_by ID
        #             })
        partner_id = self.id
        action = self.env.ref('ddl_nc_customer_credit_form.action_sold_item').read()[0]
        action['domain'] = [('customer', '=', partner_id)]
        return action


    def operational_approve(self):
        for rec in self:
            rec.status = 'o_approve'
            rec.customer_validate = False

    def finance_approve(self):
        for rec in self:
            rec.status = 'f_approve'
            rec.customer_validate = True

    def draft(self):
        for rec in self:
            rec.status = 'draft'
            rec.customer_validate = False

class ResPartnerVisit(models.Model):
    _name = 'res.partner.visit'

    partner_id = fields.Many2one('res.partner', String="Partner ID")
    customer_id = fields.Many2one('res.partner', String="Customer ID")
    lead_id = fields.Many2one('crm.lead', String="Lead ID")
    date = fields.Datetime(string="Visit Date")
    stage_id = fields.Many2one(related="lead_id.stage_id")


class ResPartnerInherited2(models.Model):
    _inherit = 'res.partner'

    brand_ids = fields.Many2many('product.brand', string='Allowed Brands')

    @api.model
    def update_module(self, module_name):
        # Get the 'module' model
        module_obj = self.env['ir.module.module']

        # Find the module you want to update
        module = module_obj.search([('name', '=', module_name)])

        # Update the module list
        module.update_list()

        # Upgrade the module immediately
        module.button_immediate_upgrade()
        print("Module Updated")


    def write(self, vals):
        record = super(ResPartnerInherited2, self).write(vals)
        if 'brand_ids' in vals and vals['brand_ids']:
            user = self.env['res.users'].search([('partner_id', '=', self.id)], limit=1)
            brands = [val.id for val in self.brand_ids]
            if user:
                user.write({'brand_ids': [(6, 0, brands)]})
                self.update_module('ddl_nc_customer_credit_form')
        if 'pharmacy_ids' in vals and vals['pharmacy_ids']:
            user = self.env['res.users'].search([('partner_id', '=', self.id)], limit=1)
            pharmacy = [val.id for val in self.pharmacy_ids]
            if user:
                user.write({'pharmacy_ids': [(6, 0, pharmacy)]})
                self.update_module('ddl_nc_customer_credit_form')
        if 'doctor_ids' in vals and vals['doctor_ids']:
            if self.not_write == False:
                doctors = self.env['res.partner'].search([('active', '=', True), ('is_doctor', '=', True)])
                for doctor1 in doctors:
                    doctor1.not_write = True
                    doctor1.pharmacy_ids = [(3, self.id)]
                    doctor1.not_write = False
                for doctor_id in self.doctor_ids:
                    doctor_id.not_write = True
                    doctor_id.pharmacy_ids = [(4, self.id)]
                    doctor_id.is_doctor = True
                    doctor_id.not_write = False

        if 'pharmacy_ids' in vals and vals['pharmacy_ids']:
            if self.not_write == False:
                if self.is_doctor == True:
                    pharmacies = self.env['res.partner'].search([('active', '=', True), ('is_a_customer', '=', True)])
                    for pharmacy1 in pharmacies:
                        pharmacy1.not_write = True
                        pharmacy1.doctor_ids = [(3, self.id)]
                        pharmacy1.not_write = False
                    for pharmacy in self.pharmacy_ids:
                        pharmacy.not_write = True
                        pharmacy.doctor_ids = [(4, self.id)]
                        pharmacy.not_write = False

    def create(self, vals):
        record = super(ResPartnerInherited2, self).create(vals)
        if record.is_doctor == True:
            record.is_company = False
        if record.is_a_salesperson == True:
            record.is_company = False
        if record.is_a_customer == True:
            record.is_company = True
        if record.is_a_vendor == True:
            record.is_company = True
        if record.is_a_hospital == True:
            record.is_company = True
        if record.is_a_clinic == True:
            record.is_company = True
        if record.doctor_ids:
            if record.not_write == False:
                doctors = self.env['res.partner'].search([('active', '=', True), ('is_doctor', '=', True)])
                for doctor1 in doctors:
                    doctor1.not_write = True
                    doctor1.pharmacy_ids = [(3, record.id)]
                    doctor1.not_write = False
                for doctor_id in record.doctor_ids:
                    doctor_id.not_write = True
                    doctor_id.pharmacy_ids = [(4, record.id)]
                    doctor_id.is_doctor = True
                    doctor_id.not_write = False

        if record.pharmacy_ids:
            if record.not_write == False:
                if record.is_doctor == True:
                    pharmacies = self.env['res.partner'].search([('active', '=', True), ('is_a_customer', '=', True)])
                    for pharmacy1 in pharmacies:
                        pharmacy1.not_write = True
                        pharmacy1.doctor_ids = [(3, record.id)]
                        pharmacy1.not_write = False
                    for pharmacy in record.pharmacy_ids:
                        pharmacy.not_write = True
                        pharmacy.doctor_ids = [(4, record.id)]
                        pharmacy.not_write = False
        return record