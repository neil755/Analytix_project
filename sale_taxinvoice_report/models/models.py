# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleTaxinvoiceReport(models.Model):
    _inherit = 'sale.order'

    def tax_amount_in_words(self, sale):
        if sale:
            for sales in sale:
                if sales.amount_total:
                    rounded_amount = round(sales.amount_total)
                    usd_value = self.currency_id.amount_to_text(rounded_amount)
                    return usd_value

    def amount_doller(self, amount):
        if amount:
            rounded_amount = round(amount)
            usd_value = self.env.ref('base.USD').amount_to_text(rounded_amount)
            return usd_value

    def get_tax_names(self):
        """Returns a string of all tax names applied to the order"""
        tax_names = []
        for line in self.order_line:
            for tax in line.tax_id:
                if tax.name not in tax_names:
                    tax_names.append(tax.name)
        return ", ".join(tax_names)

class SaleOrderLineTaxInvoice(models.Model):
    _inherit = 'sale.order.line'