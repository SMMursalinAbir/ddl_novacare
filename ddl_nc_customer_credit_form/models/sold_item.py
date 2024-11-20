from odoo import models, fields, api

class SoldItem(models.Model):
    _name = 'sold.item'
    _description = 'Sold Item'
    _rec_name = 'invoice_no'

    customer = fields.Many2one('res.partner', string='Customer')
    invoice_no = fields.Char(string='Invoice Number')
    invoice_origin = fields.Char(string='Sale Order No')
    product_id = fields.Many2one('product.product', string='Product')
    product_label = fields.Char(string='Product Label')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Price Unit')
    recommended_by = fields.Many2one('res.partner', string='Dr Recommended', domain="[('is_doctor', '=', True)]")
    recommended_quantity = fields.Float(string='Recommended Quantity')
    invoice_line_id = fields.Integer(string='Invoice line ID', readonly=True)
    invoice_date = fields.Date(string="Invoice Date")
    pharmacy_sold_quantity = fields.Integer(string="Phrmacy Sold Quantity")
    product_lot_numder = fields.Char(string="Product Lot Number", compute="compute_lot_number")
    expire_date = fields.Datetime(string='Expire Date', compute="compute_lot_number")
    delivery_date = fields.Datetime(string='Delivery Date', compute="compute_delivery_date")
    salesperson_id = fields.Many2one('res.users', string='Salesperson')
    removal_date = fields.Datetime(string='Removal Date', compute="compute_lot_number")


    def compute_lot_number(self):
        for rec in self:
            stock_move = self.env['stock.move'].search(
                [('origin', '=', rec.invoice_origin), ('product_id', '=', rec.product_id.id)], limit=1)
            stock_move_line = self.env['stock.move.line'].search(
                [('product_id', '=', rec.product_id.id), ('move_id', '=', stock_move.id)], limit=1)

            if stock_move and stock_move_line:
                stock_lot = self.env['stock.lot'].search(
                    [('product_id', '=', rec.product_id.id), ('name', '=', stock_move_line.lot_id.name)], limit=1)
                rec.product_lot_numder = stock_move_line.lot_id.name
                rec.expire_date = stock_lot.expiration_date
                rec.removal_date = stock_lot.removal_date
            else:
                rec.product_lot_numder = " "
                rec.expire_date = None
                rec.removal_date = None

    def compute_delivery_date(self):
        for rec in self:
            stock_picking = self.env['stock.picking'].search(
                [('origin', '=', rec.invoice_origin), ('state', '=', 'done')], limit=1)
            if stock_picking:
                rec.delivery_date = stock_picking.date_done
            else:
                rec.delivery_date = None

