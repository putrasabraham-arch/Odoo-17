# MRP Add Landed Cost Futake - Odoo 17

## Fungsi
Menambahkan pada form Manufacturing Order:
- tombol **Add Cost** di header: membuka form Landed Cost baru dengan
  **Apply On = Manufacturing Orders**, MO aktif terisi otomatis, company
  mengikuti MO; user tinggal menambah Cost Lines lalu Compute dan Validate.
- **smart button "Landed Costs"** di button box (bagian atas form MO):
  menampilkan jumlah Landed Cost yang terhubung ke MO dan membuka daftarnya
  (tombol hanya muncul bila sudah ada Landed Cost terkait).

## Dependensi
- `mrp_landed_costs` (modul standar Odoo 17 untuk Landed Cost pada Manufacturing Order)

## Instalasi
1. Ekstrak folder `mrp_add_landed_cost_futake` ke custom addons Odoo 17.
2. Restart service Odoo.
3. Update Apps List.
4. Install **MRP Add Landed Cost Futake**.

CLI contoh:
`./odoo-bin -d NAMA_DB -u mrp_add_landed_cost_futake --stop-after-init`

## Catatan
Tombol dan field Manufacturing Order pada Landed Cost standar Odoo dibatasi
untuk grup `stock.group_stock_manager`, sehingga kedua tombol mengikuti grup
yang sama. Jika modul lama `mrp_add_landed_cost_pni` masih terpasang di sebuah
database, uninstall dulu sebelum memasang modul ini.