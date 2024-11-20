from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError

class SalespersonTarget(models.Model):
    _name = 'salesperson.target'
    _description = 'Salesperson Target'
    _rec_name = 'salesperson'

    date_from = fields.Datetime(string='Date From', required=True)
    date_to = fields.Datetime(string='Date To', required=True)
    monthly_target = fields.Integer(string='Target', required=True)
    salesperson = fields.Many2one('res.users', string='Salesperson', required=True)
    total_sold = fields.Float(string='Total Sold', compute='_compute_total_sold')
    expected_sales = fields.Float(string="Expected Sales", compute="compute_expected_sales")
    total_sold1 = fields.Float(string='Total Sold')
    expected_sales1= fields.Float(string="Expected Sales")
    visit_target_manual = fields.Integer(string="Visit Target")
    visit_target = fields.Integer(string="Expected Visit Target", compute="expected_visit")
    total_visit = fields.Integer(string="Visit Achievement", compute="compute_total_visit")
    visit_target1 = fields.Integer(string="Visit Target")
    total_visit1 = fields.Integer(string="Total Visit")

    def expected_visit(self):
        for rec in self:
            expected_visit = self.env['crm.lead'].search_count(
                [('user_id', '=', rec.salesperson.id), ('visit_date', '>=', rec.date_from),
                 ('visit_date', '<=', rec.date_to)])
            if expected_visit:
                rec.visit_target = expected_visit
                rec.visit_target1 = rec.visit_target
            else:
                rec.visit_target = 0
                rec.visit_target1 = rec.visit_target

    def compute_total_visit(self):
        for rec in self:
            total_visit = self.env['crm.lead'].search_count(
                [('user_id', '=', rec.salesperson.id), ('visit_date', '>=', rec.date_from),
                 ('visit_date', '<=', rec.date_to), ('stage_id', '!=', 1)])
            if total_visit:
                rec.total_visit = total_visit
                rec.total_visit1 = rec.total_visit
            else:
                rec.total_visit = 0
                rec.total_visit1 = rec.total_visit


    def compute_expected_sales(self):
        for rec in self:
            expected_revenues = self.env['crm.lead'].search([('user_id','=',rec.salesperson.id)])
            if expected_revenues:
                sum = 0
                for expected_revenue in expected_revenues:
                    if rec.date_from <= expected_revenue.visit_date and rec.date_to >= expected_revenue.visit_date:
                        sum = sum + expected_revenue.expected_revenue
                rec.expected_sales = sum
                rec.expected_sales1 = rec.expected_sales
            else:
                rec.expected_sales = 0
                rec.expected_sales1 = rec.expected_sales


    @api.depends('salesperson')
    def _compute_total_sold(self):
        for record in self:
            if record.monthly_target > 0:
                if record.salesperson:
                    # start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    # end_date = start_date + relativedelta(months=1)
                    total_amount = self.env['sale.order'].search([
                        ('user_id', '=', record.salesperson.id),
                        ('state', '=', 'sale'),
                        ('date_order', '>=', record.date_from),
                        ('date_order', '<', record.date_to)
                    ]).mapped('amount_total')
                    record.total_sold = sum(total_amount)
                    record.total_sold1 = record.total_sold
                else:
                    record.total_sold = 0
                    record.total_sold1 = record.total_sold
            else:
                record.total_sold = 0
                record.total_sold1 = record.total_sold

    @api.constrains('date_from', 'date_to')
    def _check_model(self):
        for record in self:
            if record.date_from > record.date_to:
                raise ValidationError(_('Enter Valid Date'))
