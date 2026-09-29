from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    receipt_reference = fields.Char(
        string='Referensi',
        help="Referensi untuk Bukti Penerimaan Barang. "
             "Jika kosong, akan fallback ke Vendor Reference dari Purchase Order terkait.",
    )
    receipt_note = fields.Text(
        string='Catatan Penerimaan',
        help="Catatan yang ditampilkan pada bagian Catatan Bukti Penerimaan Barang.",
    )
    delivered_by = fields.Char(
        string='Diserahkan Oleh',
        help="Nama pihak yang menyerahkan barang (untuk Bukti Penerimaan Barang).",
    )
    received_by = fields.Char(
        string='Diterima Oleh',
        default=lambda self: self.env.user.name,
        help="Nama pihak yang menerima barang (untuk Bukti Penerimaan Barang).",
    )
    approved_by = fields.Char(
        string='Mengetahui',
        help="Nama pihak yang mengetahui/menyetujui penerimaan barang.",
    )
    receipt_vendor_ref = fields.Char(
        string='Vendor Reference',
        compute='_compute_receipt_vendor_ref',
        help="Vendor Reference dari Purchase Order terkait, diambil dari relasi standar "
             "stock.move -> purchase.line -> purchase.order.",
    )

    @api.depends('move_ids_without_package.purchase_line_id.order_id.partner_ref')
    def _compute_receipt_vendor_ref(self):
        for picking in self:
            orders = picking.move_ids_without_package.mapped('purchase_line_id.order_id')
            picking.receipt_vendor_ref = orders[:1].partner_ref or False

    def action_print_bukti_penerimaan(self):
        self.ensure_one()
        return self.env.ref(
            'custom_receipt_bukti_penerimaan_futake.action_report_bukti_penerimaan'
        ).report_action(self)


class StockMove(models.Model):
    _inherit = 'stock.move'

    receipt_remark = fields.Char(
        string='Keterangan',
        help="Keterangan per baris barang untuk Bukti Penerimaan Barang "
             "(contoh: Barang baik, Kurang 2 pcs, 1 pcs penyok).",
    )