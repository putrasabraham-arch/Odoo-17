# -*- coding: utf-8 -*-
# Part of sale_downpayment_account. See LICENSE file for full copyright and licensing details.
# Author: https://github.com/putrasabraham-arch

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    down_payment_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Down Payment Account",
        domain=[
            ('account_type', 'not in', ('asset_receivable', 'liability_payable')),
            ('deprecated', '=', False),
        ],
        check_company=True,
        copy=False,
        help="Account used on the invoice line of this down payment, both when "
             "creating the down payment invoice and when the final invoice "
             "deducts this down payment.")

    def _prepare_invoice_line(self, **optional_values):
        # EXTENDS sale
        self.ensure_one()
        values = super()._prepare_invoice_line(**optional_values)
        if self.is_downpayment and not self.display_type and self.down_payment_account_id:
            values['account_id'] = self.down_payment_account_id.id
        return values