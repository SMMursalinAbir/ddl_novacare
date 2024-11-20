from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('partner_id')
    def check_partner(self):
        for rec in self:
            if rec.partner_id.customer_validate != True :
                raise ValidationError(_('The Pharmacy is  not Verified'))
            if (rec.partner_id.is_a_customer != True and rec.partner_id.is_a_vendor != True):
                raise ValidationError(_('This is not a pharmacy/vendor'))





class Inventory(models.Model):
    _inherit = 'stock.picking'

    @api.constrains('partner_id')
    def check_partner(self):
        for rec in self:
            if rec.partner_id.customer_validate != True:
                raise ValidationError(_('The Pharmacy is  not Verified'))




class CustomAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    lot_number = fields.Char(string='Lot Number', help='Lot Number for the product', compute="compute_lot_number")
    expire_date = fields.Datetime(string='Expiry DT', compute="compute_lot_number")
    vat_amount = fields.Float(string="Vat Amount", compute="compute_vat_amount")
    discount_amount = fields.Float(string="Discount Amount", compute="compute_discount_amount")


    def compute_lot_number(self):
        for rec in self:
            stock_move = self.env['stock.move'].search([('origin', '=', rec.move_id.invoice_origin),('product_id','=', rec.product_id.id)], limit=1)
            stock_move_line = self.env['stock.move.line'].search([('product_id', '=', rec.product_id.id),('move_id', '=', stock_move.id)], limit=1)

            if stock_move and stock_move_line:
                stock_lot = self.env['stock.lot'].search(
                    [('product_id', '=', rec.product_id.id), ('name', '=', stock_move_line.lot_id.name)], limit=1)
                rec.lot_number = stock_move_line.lot_id.name
                rec.expire_date = stock_lot.expiration_date
            else:
                rec.lot_number = " "
                rec.expire_date = None

    def compute_vat_amount(self):
        for rec in self:
            rec.vat_amount = rec.price_total - rec.price_subtotal

    def compute_discount_amount(self):
        for rec in self:
            if rec.discount != 0:
                discount_price = (rec.price_unit * rec.quantity)*(rec.discount/100)
                rec.discount_amount = discount_price
            else:
                rec.discount_amount = 0

class CustomAccountMove(models.Model):
    _inherit = 'account.move'
    amount_untaxed_word = fields.Char(string="Amount Untaxed", compute="compute_numbers_to_word")
    amount_tax_word = fields.Char(string="Amount Tax", compute="compute_numbers_to_word")
    amount_total_word = fields.Char(string="Amount Total", compute="compute_numbers_to_word")
    has_warning = fields.Boolean(string="Has Warning")

    @api.depends('company_id', 'partner_id', 'tax_totals', 'currency_id')
    def _compute_partner_credit_warning(self):
        res = super(CustomAccountMove, self)._compute_partner_credit_warning()
        for move in self:
            move.with_company(move.company_id)
            move.partner_credit_warning = ''
            show_warning = move.state == 'draft' and \
                           move.move_type == 'out_invoice' and \
                           move.company_id.account_use_credit_limit
            if show_warning:
                move.partner_credit_warning = self._build_credit_warning_message(
                    move,
                    current_amount=move.tax_totals['amount_total'],
                    exclude_current=True,
                )
                self.has_warning = True
            if move.partner_credit_warning == '':
                self.has_warning = False
        return res


    def action_post(self):
        res = super(CustomAccountMove, self).action_post()
        if self.partner_id.post_restriction_on_credit:
            if self.has_warning == True:
                raise ValidationError(_("Customer Credit limit has been exeeded"))
        return res


    def write(self, vals):
        record = super(CustomAccountMove, self).write(vals)
        if 'state' in vals and vals['state']:
            for rec in self:
                if rec.state == 'posted' and rec.move_type == 'out_invoice':
                    for invoice_line in rec.invoice_line_ids:
                        x = invoice_line.product_id.id
                        print(x)
                        if invoice_line.product_id:
                            vals = {
                                'customer': rec.partner_id.id,
                                'salesperson_id': rec.invoice_user_id.id,
                                'invoice_no': rec.name,
                                'invoice_origin': rec.invoice_origin,
                                'invoice_line_id': invoice_line.id,
                                'product_id': invoice_line.product_id.id,
                                'product_label': invoice_line.product_id.name,
                                'quantity': invoice_line.quantity,
                                'price_unit': invoice_line.price_unit,
                                'invoice_date': invoice_line.invoice_date,
                            }
                            self.env['sold.item'].create(vals)

    def convert_number_to_words(self, number):
        if number == 0:
            return "Zero"

        # Define the word representations for each power of 10
        powers_of_ten = ["", "Thousand", "Million", "Billion", "Trillion", "Quadrillion", "Quintillion", "Sextillion"]

        # Function to convert a number less than 1000 to words
        def convert_below_thousand(num):
            units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
            teens = ["", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen",
                     "Nineteen"]
            tens = ["", "Ten", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

            if num < 10:
                return units[num]
            elif num < 20:
                return teens[num - 10]
            elif num < 100:
                return tens[num // 10] + (" " + units[num % 10] if num % 10 != 0 else "")
            else:
                return units[num // 100] + " Hundred" + (
                    " and " + convert_below_thousand(num % 100) if num % 100 != 0 else "")

        integer_part = int(number)
        decimal_part = int(round((number - integer_part) * 100))  # Corrected for accurate rounding

        result = ""
        power_index = 0

        while integer_part > 0:
            chunk = integer_part % 1000
            if chunk != 0:
                result = convert_below_thousand(chunk) + (
                    " " + powers_of_ten[power_index] if power_index > 0 else "") + " " + result
            integer_part //= 1000
            power_index += 1

        result = result.strip()

        if decimal_part > 0:
            result += f" and {convert_below_thousand(decimal_part)} fils"

        return result


    def compute_numbers_to_word(self):
        for rec in self:
            amount_untaxed = rec.convert_number_to_words(rec.amount_untaxed)
            amount_tax = rec.convert_number_to_words(rec.amount_tax)
            amount_total = rec.convert_number_to_words(rec.amount_total)

            rec.amount_untaxed_word = amount_untaxed
            rec.amount_tax_word = amount_tax
            rec.amount_total_word = amount_total






