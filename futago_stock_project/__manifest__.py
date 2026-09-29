# -*- coding: utf-8 -*-
{
    'name': 'Futago Stock Project',
    'version': '17.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Auto-create Project/Task from Storable products on SO confirmation',
    'description': """
Storable products keep the standard Inventory flow, but confirming a
Sales Order can automatically generate a Project and/or Tasks, similar
to the "Create on Order" concept of Service products.
    """,
    'author': 'Futago',
    'license': 'LGPL-3',
    'depends': [
        'sale_management',
        'sale_project',
        'project',
        'stock',
    ],
    'data': [
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}