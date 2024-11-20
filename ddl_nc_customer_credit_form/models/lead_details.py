from odoo import models, fields, api
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class LeadDetails(models.Model):
    _name = 'lead.details'
    _description = 'Lead Details'

    lead_name = fields.Many2one('crm.lead', string='Lead ID', required=True)
    salesperson = fields.Many2one('res.users', string='Salesperson')
    date = fields.Datetime(string='Date')
    customer = fields.Many2one('res.partner', string='Customer')
    sales_team = fields.Many2one('crm.team', string='Sales Team')
    sale_order_count = fields.Integer(string='Sale Orders', compute='compute_sale_order_count')
    sale_order_count1 = fields.Integer(string='Sale Orders')

    def compute_sale_order_count(self):
        for rec in self:
            if rec.lead_name:
                count = self.env['sale.order'].search_count([('origin', '=', rec.lead_name.name)])
                rec.sale_order_count = count
                rec.sale_order_count1 = rec.sale_order_count
            else:
                rec.sale_order_count = 0
                rec.sale_order_count1 = rec.sale_order_count


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    visit_date = fields.Datetime(string="Scheduled Visit Date", required=True)

    def crm_lead_refresh(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'CRM Lead',
            'res_model': 'crm.lead',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def write(self, vals):
        for rec in self:
            result = super(CrmLead, self).write(vals)

            if 'stage_id' in vals and self.stage_id.sequence == 2:
                # Create lead.details record
                customer = self.env['res.partner'].search([('id', '=', rec.partner_id.id)], limit=1)
                if customer:
                    customer.crm_lead_count = customer.crm_lead_count + 1
                existing_lead_details = self.env['lead.details'].search([('lead_name', '=', rec.id),('date', '=', rec.create_date)], limit=1)
                if not existing_lead_details:
                    lead_details_vals = {
                        'lead_name': rec.id,
                        'salesperson': rec.user_id.id,
                        'date': rec.create_date,
                        'customer': rec.partner_id.id,
                        'sales_team': rec.team_id.id,
                    }

                    self.env['lead.details'].create(lead_details_vals)

            return result


    @api.model
    def create(self, vals):
        lead = super(CrmLead, self).create(vals)
        if vals.get('type') == 'opportunity':
            user_id = vals.get('user_id') or lead.user_id.id
            if user_id:
                model_id = self.env['ir.model'].search([('model', '=', 'crm.lead')], limit=1).id
                activity_values = {
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': "LEAD VISIT REMINDER",
                    'note': "Please Visit The Customer",
                    'res_id': lead.id,
                    'res_model_id': model_id,
                    'user_id': user_id,
                    'date_deadline': lead.visit_date,
                }
                try:
                    self.env['mail.activity'].create(activity_values)
                    _logger.info("ACTIVITY CREATED SUCCESSFULLY")
                except Exception as e:
                    _logger.error(f"Failed to create activity: {e}")
        return lead

class Lead2OpportunityPartnerInherit(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    def action_apply(self):
        result_opportunity = super(Lead2OpportunityPartnerInherit, self).action_apply()
        if result_opportunity:
            lead_ids = self.env.context.get('active_ids', [])
            leads = self.env['crm.lead'].browse(lead_ids)
            for lead in leads:
                if lead.type == 'opportunity':
                    model_id = self.env['ir.model'].search([('model', '=', 'crm.lead')], limit=1).id
                    activity_values = {
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'summary': "LEAD VISIT REMINDER",
                        'note': "Please Visit The Customer",
                        'res_id': lead.id,
                        'res_model_id': model_id,
                        'user_id': lead.user_id.id,
                        'date_deadline': lead.visit_date,
                    }
                    try:
                        self.env['mail.activity'].create(activity_values)
                        _logger.info("ACTIVITY CREATED SUCCESSFULLY")
                    except Exception as e:
                        _logger.error(f"Failed to create activity: {e}")
        return result_opportunity



class MailActivity(models.Model):
    _inherit = 'mail.activity'


    def action_feedback(self, feedback=False, attachment_ids=None):
        if self.res_model == 'crm.lead' and self.summary == "LEAD VISIT REMINDER":
            # self.crm_lead_refresh()
            crm_lead = self.env['crm.lead'].search([('id', '=', int(self.res_id))], limit=1)
            crm_stage = self.env['crm.stage'].search([('sequence', '=', 2)], limit=1)
            if crm_lead and crm_stage:
                # crm_lead.stage_id = crm_stage.id
                vals = {
                    'stage_id': crm_stage.id
                }
                crm_lead.write(vals)
                crm_lead.crm_lead_refresh()
        return super(MailActivity, self).action_feedback()

class CrmTeamInherit(models.Model):
    _inherit = 'crm.team'

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
        record = super(CrmTeamInherit, self).write(vals)
        print(self.member_ids)
        admin = self.env['res.users'].search([('name', '=', 'Administrator')], limit=1)
        if 'member_ids' in vals and vals['member_ids'] and admin:
            user = self.env['res.users'].search([('id', '=', self.user_id.id)], limit=1)
            if user:
                members = [val.id for val in self.member_ids]
                user.write({'user_ids': [(6, 0, [admin.id] + members)]})

    @api.model
    def create(self, vals):
        record = super(CrmTeamInherit, self).create(vals)
        if 'member_ids' in vals and vals['member_ids']:
            user = self.env['res.users'].search([('id', '=', record.user_id.id)], limit=1)
            admin = self.env['res.users'].search([('name', '=', 'Administrator')], limit=1)
            if user and admin:
                members = [val.id for val in record.member_ids]
                user.write({'user_ids': [(6, 0, [admin.id] + members)]})
        return record

