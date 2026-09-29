{
    'name': 'Custom Receipt - Bukti Penerimaan Barang',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Tombol & Report PDF "Bukti Penerimaan Barang" untuk Receipt (Incoming Shipment)',
    'description': """
Custom minimal untuk Odoo 17:
- Field khusus Bukti Penerimaan pada stock.picking
- Field Keterangan per baris Operations pada stock.move
- Tombol "Cetak Bukti Penerimaan Barang" di header form Receipt (hanya incoming + done)
- Report QWeb PDF A4 Portrait menyerupai formulir Bukti Penerimaan Barang
""",
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': ['stock', 'purchase', 'purchase_stock'],
    'data': [
        'report/report_action.xml',
        'views/stock_picking_views.xml',
        'report/report_bukti_penerimaan.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}