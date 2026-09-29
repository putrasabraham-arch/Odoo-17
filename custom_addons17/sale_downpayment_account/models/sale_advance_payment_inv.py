# -*- coding: utf-8 -*-
# Part of sale_downpayment_account. See LICENSE file for full copyright and licensing details.
# Author: https://github.com/putrasabraham-arch

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    down_payment_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Down Payment Account",
        domain=[
            ('account_type', 'not in', ('asset_receivable', 'liability_payable')),
            ('deprecated', '=', False),
        ],
        check_company=True,
        help="Account used on the down payment invoice line and on the line "
             "deducting this down payment in the final invoice. The income "
             "account of the Down Payment product is left unchanged.")

    #=== CONSTRAINT METHODS ===#

    @api.constrains('advance_payment_method', 'down_payment_account_id')
    def _check_down_payment_account(self):
        for wizard in self:
            if wizard.advance_payment_method not in ('percentage', 'fixed'):
                continue
            if not wizard.down_payment_account_id:
                raise UserError(_("Please select a Down Payment Account before "
                                  "creating the down payment invoice."))
            if wizard.down_payment_account_id.account_type in ('asset_receivable', 'liability_payable'):
                raise UserError(_("The Down Payment Account cannot be a "
                                  "receivable or payable account."))

    #=== BUSINESS METHODS ===#

    def _prepare_base_downpayment_line_values(self, order):
        # EXTENDS sale
        self.ensure_one()
        values = super()._prepare_base_downpayment_line_values(order)
        values['down_payment_account_id'] = self.down_payment_account_id.id
        return values