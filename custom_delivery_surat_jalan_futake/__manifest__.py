{
    'name': 'Custom Delivery - Surat Jalan Pengiriman',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Tombol & Report PDF "Surat Jalan Pengiriman" untuk Delivery Order (Outgoing Shipment)',
    'description': """
Custom minimal untuk Odoo 17:
- Field khusus Surat Jalan pada stock.picking (kendaraan, driver, penerima, dll)
- Field Berat (Kg) & Keterangan per baris Operations pada stock.move
- Field default Catatan Penting pada res.company
- Tombol "Cetak Surat Jalan Pengiriman" di header form Delivery Order
  (hanya outgoing + assigned/done)
- Report QWeb PDF A4 Landscape menyerupai formulir Surat Jalan Pengiriman
""",
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': ['stock', 'sale_stock'],
    'data': [
        'report/paperformat.xml',
        'report/report_action.xml',
        'views/stock_picking_views.xml',
        'report/report_surat_jalan.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}