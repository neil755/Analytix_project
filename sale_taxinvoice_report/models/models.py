# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleTaxinvoiceReport(models.Model):
    _inherit = 'sale.order'

    def tax_amount_in_words(self, sale):
        if sale:
            for sales in sale:
                if sales.amount_total:
                    usd_value = self.currency_id.amount_to_text(sales.amount_total)
                    return usd_value

class SaleOrderLineTaxInvoice(models.Model):
    _inherit = 'sale.order.line'
