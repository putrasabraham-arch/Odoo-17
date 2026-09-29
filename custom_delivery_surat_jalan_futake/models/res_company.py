from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    delivery_note_default = fields.Text(
        string='Catatan Penting Surat Jalan',
        help="Teks default bagian 'CATATAN PENTING' pada report Surat Jalan Pengiriman. "
             "Jika kosong, digunakan teks default dari module.",
    )