from odoo import api, fields, models
from odoo.tools import format_date as format_date_tool


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    vehicle_number = fields.Char(
        string='Nomor Polisi',
        help="Nomor polisi kendaraan pengiriman (contoh: AD 1234 XX).",
    )
    vehicle_type = fields.Char(
        string='Jenis Kendaraan',
        help="Jenis kendaraan pengiriman (contoh: Pickup, Truck, Engkel).",
    )
    driver_name = fields.Char(
        string='Driver',
        help="Nama driver pengiriman.",
    )
    receiver_name = fields.Char(
        string='Penerima',
        help="Nama pihak yang menerima barang.",
    )
    security_name = fields.Char(
        string='Security',
        help="Nama petugas security.",
    )
    production_head_name = fields.Char(
        string='Kepala Produksi',
        help="Nama kepala produksi.",
    )
    marketing_name = fields.Char(
        string='Marketing',
        help="Nama pihak marketing.",
    )
    delivery_note = fields.Text(
        string='Catatan Surat Jalan',
        help="Catatan tambahan yang ditampilkan pada report Surat Jalan Pengiriman.",
    )
    delivery_so_ref = fields.Char(
        string='Referensi SO',
        compute='_compute_delivery_so_ref',
        help="Nomor Sales Order terkait, dari relasi standar sale_id.",
    )

    def _get_delivery_date(self):
        """Tanggal kirim: date_done jika Done, scheduled_date jika belum."""
        self.ensure_one()
        return self.date_done if self.state == 'done' else self.scheduled_date

    def _get_delivery_date_str(self):
        """Tanggal kirim dalam format Indonesia yang rapi (contoh: 23 Juli 2026)."""
        self.ensure_one()
        value = self._get_delivery_date()
        if not value:
            return ''
        return format_date_tool(self.env, value, lang_code='id_ID', date_format='dd MMMM yyyy')

    @api.depends('sale_id.name')
    def _compute_delivery_so_ref(self):
        for picking in self:
            picking.delivery_so_ref = picking.sale_id.name or False

    def action_print_surat_jalan_pengiriman(self):
        self.ensure_one()
        return self.env.ref(
            'custom_delivery_surat_jalan_futake.action_report_surat_jalan'
        ).report_action(self)


class StockMove(models.Model):
    _inherit = 'stock.move'

    delivery_weight = fields.Float(
        string='Berat (Kg)',
        help="Berat barang khusus untuk Surat Jalan Pengiriman (input manual). "
             "Tidak mempengaruhi berat standar product.",
    )
    delivery_remark = fields.Char(
        string='Keterangan',
        help="Keterangan per baris barang untuk Surat Jalan Pengiriman.",
    )