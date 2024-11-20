from odoo import models, fields, api
from datetime import datetime
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
class StockReturn(models.TransientModel):
    _inherit = 'stock.return.picking'

    return_reason = fields.Char(string="Return Reason")
    return_type = fields.Selection([('create_credit_note', 'Create Credit Note'),
                              ('replacement', 'Replacement'),
                              ], string='Return Type', default='replacement')
    def _prepare_picking_default_values(self):
        vals = super(StockReturn, self)._prepare_picking_default_values()
        return_picking_id = self.env['stock.picking.type'].search([('name', '=', "Returned")], limit=1)
        if return_picking_id:
            vals['picking_type_id'] = return_picking_id.id
            vals['return_reason'] = self.return_reason
            vals['return_type'] = self.return_type
            vals['user_id'] = self.picking_id.user_id.id
            vals['check_redeliver'] = False
            if self.picking_id.check_redeliver == True:
                vals['check_redeliver_return'] = True
        return vals

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    return_reason = fields.Char(string="Return Reason")
    return_type = fields.Selection([
        ('create_credit_note', 'Create Credit Note'),
        ('replacement', 'Replacement'),
    ], string='Return Type', default='replacement')
    check_return = fields.Boolean(string="Check Return", compute="compute_check_return")
    check_redeliver = fields.Boolean(string="check_redeliver", default=False)
    check_redeliver_return = fields.Boolean(string="check redeliver return", default=False)



    @api.model
    def create(self, values):
        if not values['user_id']:
            if values['origin']:
                origin = values['origin']
                so = self.env['sale.order'].search([('name', '=', origin)], limit=1)
                values['user_id'] = so.user_id.id
        return super(StockPicking, self).create(values)

    @api.depends('picking_type_id.name')
    def compute_check_return(self):
        for record in self:
            if record.picking_type_id.name == "Returned":
                record.check_return = True
            else:
                record.check_return = False

    def action_redeliver(self):
        for rec in self:
            new_picking = self.env['stock.picking'].create({
                'partner_id': rec.partner_id.id,
                'picking_type_id': 2,
                'location_id': rec.location_dest_id.id,
                'user_id': rec.user_id.id,
                'origin': rec.group_id.name,
                'check_redeliver': True,
            })
            move_ids = []
            for line in rec.move_ids:
                new_move = self.env['stock.move'].create({
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'quantity': line.quantity,
                    'product_uom': line.product_uom.id,
                    'location_id': line.location_id.id,
                    'location_dest_id': line.location_dest_id.id,
                    'picking_id': new_picking.id,
                })
                move_ids.append((4, new_move.id))
                move_line = self.env['stock.move.line'].search([('move_id','=',new_move.id)], limit=1)
                move_line_product_lot = self.env['stock.move.line'].search([('origin', '=', rec.group_id.name),('lot_id', '!=', False),('product_id','=', line.product_id.id)], limit=1)
                if move_line:
                    vals = {
                        'location_id' : line.location_dest_id.id,
                        'location_dest_id': line.location_id.id,
                        'lot_id': move_line_product_lot.lot_id.id,
                    }

                    x = move_line.write(vals)


            vals = {
                'group_id': rec.group_id.id,
                'move_ids': move_ids,
                'sale_id': rec.sale_id.id,

            }
            new_picking.write(vals)
            new_picking.group_id = rec.group_id.id
            new_picking.sale_id = rec.sale_id.id
            action = {
                'name': 'New Picking',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'form',
                'res_id': new_picking.id,
            }
        return action


    @api.onchange('state')
    def state_change(self):
        if self.state == 'done':
            print("success")

    def button_validate(self):
        vals = super(StockPicking, self).button_validate()
        if self.check_redeliver == True:
            products = [val for val in self.move_ids]
            if products:
                so = self.env['sale.order'].search([('name', '=', self.group_id.name)], limit=1)
                if so:
                    for so_line in so.order_line:
                        for product in products:
                            if so_line.product_id.id == product.product_id.id:
                                so_line.qty_delivered = so_line.qty_delivered + product.quantity

        if self.check_redeliver_return == True:
            products = [val for val in self.move_ids]
            if products:
                so = self.env['sale.order'].search([('name', '=', self.group_id.name)], limit=1)
                if so:
                    for so_line in so.order_line:
                        for product in products:
                            if so_line.product_id.id == product.product_id.id:
                                so_line.qty_delivered = so_line.qty_delivered - product.quantity
        return vals









class StockProductReturn(models.Model):
    _name = 'stock.product.return'
    _description = 'Stock Product Return'

    product = fields.Many2one('product.product', string='Product', required=True)
    demand = fields.Integer(string='Demand')
    quantity = fields.Integer(string='Quantity', required=True)
    picking_id = fields.Many2one('stock.picking', string='Picking')
    scheduled_date = fields.Datetime(string='Scheduled Date')
    partner_id = fields.Many2one('res.partner', string='Customer')
    location_dest_id = fields.Many2one('stock.location', string='Destination Location')
    source_document = fields.Char(string='Source Document')
    source = fields.Char(string='Source')
    user_id = fields.Many2one('res.users', string='Resposible')
    return_reason = fields.Char(string="Return Reason")
    return_type = fields.Selection([
        ('create_credit_note', 'Create Credit Note'),
        ('replacement', 'Replacement'),
    ], string='Return Type', default='replacement')
    state = fields.Char(string='State')

class GenerateProductReturnReport(models.TransientModel):
    _name = 'generate.product.return.report'
    _description = 'Generate Product Return Report'

    def action_product_return_report(self):
        stock_picking_type = self.env['stock.picking.type'].search([('name', '=', 'Returned')], limit=1)
        stock_pickings = self.env['stock.picking'].search([('picking_type_id', '=', stock_picking_type.id)])
        report = self.env['stock.product.return']
        self.env['stock.product.return'].search([]).unlink()
        #move_ids_without_package
        for stock_picking in stock_pickings:
            for move_id in stock_picking.move_ids_without_package:
                vals = {
                    'product' : move_id.product_id.id,
                    'demand' : move_id.product_uom_qty,
                    'quantity': move_id.quantity,
                    'picking_id': stock_picking.id,
                    'scheduled_date': stock_picking.scheduled_date,
                    'partner_id': stock_picking.partner_id.id,
                    'location_dest_id': stock_picking.location_dest_id.id,
                    'source_document': stock_picking.origin,
                    'source': stock_picking.group_id.name,
                    'user_id': stock_picking.user_id.id,
                    'return_reason': stock_picking.return_reason,
                    'return_type': stock_picking.return_type,
                    'state': str(stock_picking.state),

                }
                report.create(vals)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Product Return Report',
            'res_model': 'stock.product.return',
            'view_mode': 'tree,form,pivot',
        }


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    @api.model
    def create(self, values):
        res =  super(StockMoveInherit, self).create(values)
        ref = res.reference
        picking_id = self.env['stock.picking'].search([('name', '=', ref)], limit=1)
        if picking_id:
            if picking_id.check_redeliver_return:
                res.group_id = picking_id.return_id.group_id.id
                res.location_id = picking_id.return_id.location_dest_id.id
                res.location_dest_id = picking_id.return_id.location_id.id


        return res