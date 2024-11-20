from odoo import models, fields, api



class ResPartnerInherited(models.Model):
    _inherit = 'res.partner'


    @api.onchange('credit_limit')
    def check_credit_limit(self):
        if self.credit_limit:
            company_id = self.env.company
            company_id.account_use_credit_limit = True
            self.use_partner_credit_limit = True
