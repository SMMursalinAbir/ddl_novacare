from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import geocoder

class SalesPersonLocation(models.Model):
    _inherit = 'crm.lead'
    salesperson_latitude = fields.Char(string="SalesPerson Latitude")
    salesperson_longitude = fields.Char(string="SalesPerson Longitude")
    visit_status = fields.Selection([('visited', 'Visited'), ('not_visited', 'Not Visited')], string = 'Visit Status', default='not_visited', compute="check_visit_status")

    def check_visit_status(self):
        for rec in self:
            if rec.partner_id:
                customer_latitude = rec.partner_id.partner_latitude
                customer_longitude = rec.partner_id.partner_longitude
                salesperson_latitude = rec.salesperson_latitude
                salesperson_longitude = rec.salesperson_longitude
                if customer_latitude and customer_longitude and salesperson_latitude and salesperson_longitude:
                    s_lat = float(salesperson_latitude)
                    s_lon = float(salesperson_longitude)
                    lat_diff = customer_latitude - s_lat
                    lon_diff = customer_longitude - s_lon
                    if abs(lat_diff) < 0.07 and abs(lon_diff) < 0.07:
                        rec.visit_status = 'visited'
                        partner_visit = self.env['res.partner.visit']
                        current_date = datetime.now()
                        vals = {
                            'partner_id': rec.user_id.partner_id.id,
                            'lead_id': rec.id,
                            'customer_id': rec.partner_id.id,
                            'date': current_date,
                        }
                        partner_visit_search = self.env['res.partner.visit'].search([('partner_id','=', self.user_id.partner_id.id),('lead_id', '=', self.id)], limit=1)
                        if not partner_visit_search:
                            partner_visit.create(vals)

                    else:
                        rec.visit_status = 'not_visited'
                else:
                    rec.visit_status = 'not_visited'

            else:
                rec.visit_status = 'not_visited'


    def get_partner_location(self):
        # Use the 'ipinfo' geocoder to get the current location based on IP address
        location = geocoder.ipinfo('me')
        print(location)
        current_location = location.latlng
        print(current_location)
        if current_location:
            latitude, longitude = current_location
            print("Latitude:", latitude)
            print("Longitude:", longitude)
            partner = self.env['res.partner'].search([
                ('id', '=', self.user_id.partner_id.id),
            ], limit=1)
            lead = self.env['crm.lead'].search([('id','=', self.id)],limit=1)
            vals = {
                'salesperson_latitude': latitude,
                'salesperson_longitude' : longitude,
            }
            lead.write(vals)
            self.crm_lead_refresh()
        else:
            print("Failed to retrieve current location.")

    def action_map(self):
        # self.partner_id.partner_latitude = 37.5304271
        # self.partner_id.partner_longitude = -121.9746713
        # print(self.partner_id.partner_latitude)
        # print(self.partner_id.partner_longitude)
        self.env['crm.salesperson'].search([]).unlink()
        partner = self.env['res.partner'].search([
            ('id', '=', self.user_id.partner_id.id),
        ], limit=1)
        if self.salesperson_latitude and self.salesperson_latitude:
            partner.partner_latitude = self.salesperson_latitude
            partner.partner_longitude = self.salesperson_longitude
        salesperson_partner_id = self.user_id.partner_id.id
        new_salesperson = self.env['crm.salesperson'].create({
            'partner_id': salesperson_partner_id
        })
        action = self.env.ref('ddl_get_location.action_view_salesperson').read()[0]
        return action

    # def action_map(self):
    #     # Create a new record with partner_id set to self.partner_id.id
    #     new_salesperson = self.env['crm.salesperson'].create({
    #         'partner_id': self.partner_id.id
    #     })
    #
    #     # Return the action to view the map
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Salesperson Location Map',
    #         'res_model': 'crm.salesperson',
    #         'view_mode': 'map',
    #         # 'res_id': new_salesperson.id,
    #         'target': 'new',
    #     }


class SalesPersonMap(models.Model):
    _name = 'crm.salesperson'
    _rec_name = 'partner_id'
    partner_id = fields.Many2one('res.partner', string="Sales Person")

class CrmSalesPersonVisit(models.Model):
    _name = 'crm.salesperson.visit'

    lead_id = fields.Many2one('crm.lead', string='Lead ID')
    partner_id = fields.Many2one('res.partner', string='Partner ID')
    date = fields.Datetime(string="Date")




