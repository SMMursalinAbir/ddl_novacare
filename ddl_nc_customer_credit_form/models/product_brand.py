from odoo import models, fields, api

class ProductBrand(models.Model):
    _name = 'product.brand'
    _rec_name = 'brand_name'

    brand_name = fields.Char(string="Brand")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand', string="Brand")




    def write(self, vals):
        # Check if brand_id is being updated
        if 'brand_id' in vals:
            # Update brand_id in product.product for all variants of the template
            product_variants = self.product_variant_ids
            product_variants.write({'brand_id': vals['brand_id']})

        # Call the super method to complete the write process
        return super(ProductTemplate, self).write(vals)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('product.brand', string="Brand")


    @api.model
    def create(self, vals):
        # Call the super method to create the product and get the product record
        product = super(ProductProduct, self).create(vals)

        # Check if the product has a template and the template has a brand_id
        if product.product_tmpl_id and product.product_tmpl_id.brand_id:
            # Set the brand_id of the product based on the template's brand_id
            product.write({'brand_id': product.product_tmpl_id.brand_id.id})

        return product


class ResUsers(models.Model):
    _inherit = 'res.users'

    brand_ids = fields.Many2many('product.brand', string='Allowed Brands')
    # pharmacy_ids = fields.Many2many(related="partner_id.pharmacy_ids", string="Allowed Pharmacy")
    pharmacy_ids = fields.Many2many('res.partner', string="Allowed Pharmacy")
    user_id = fields.Many2one('res.users', string="User ID")
    user_ids = fields.Many2many('res.users', string="Team members", relation="user_id_rel",
                                column1="user_id")

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

    @api.model
    def create(self, vals):
        res_user = super(ResUsers, self).create(vals)
        admin = self.env['res.users'].search([('name', '=', 'Administrator')], limit=1)
        if admin:
            res_user.write({
                'user_ids': [(6, 0, [admin.id])]
            })
        if 'user_ids' in vals:
            self.update_module('ddl_nc_customer_credit_form')

        return res_user

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if 'user_ids' in vals:
            self.update_module('ddl_nc_customer_credit_form')
        return res
