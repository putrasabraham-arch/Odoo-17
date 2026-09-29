# -*- coding: utf-8 -*-
# Part of sale_downpayment_account. See LICENSE file for full copyright and licensing details.
# Author: https://github.com/putrasabraham-arch

{
    'name': 'Sale Down Payment Account',
    'version': '17.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Choose a specific Down Payment account on the down payment wizard',
    'description': """
Sale Down Payment Account
=========================
Adds a Down Payment Account selection on the "Create Invoice > Down payment"
wizard (Sales Order). The selected account is stored on the sale order line
down payment and is used:

* when the down payment invoice is created;
* when the final invoice deducts the down payment.

The income account of the Down Payment product master is left untouched.
""",
    'author': 'https://github.com/putrasabraham-arch',
    'website': 'https://github.com/putrasabraham-arch',
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_advance_payment_inv_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}