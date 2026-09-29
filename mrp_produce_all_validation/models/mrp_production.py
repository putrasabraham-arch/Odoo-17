# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_pending_component_pickings(self):
        """Internal component transfers of this MO that are not done yet.

        Sources of transfers:
        - `picking_ids`: all transfers sharing the MO procurement group;
        - direct link: transfers feeding `move_raw_ids`
          (`move_raw_ids.move_orig_ids.picking_id`).
        Only internal transfers that feed the component moves are blocking,
        so downstream transfers (delivery of finished goods, ...) are
        ignored.
        """
        self.ensure_one()
        component_moves = self.move_raw_ids.move_orig_ids
        pickings = self.picking_ids | component_moves.picking_id
        return pickings.filtered(
            lambda picking: (
                picking.picking_type_id.code == "internal"
                and picking.state != "done"
                and picking.move_ids & component_moves
            ))

    def button_mark_done(self):
        for production in self:
            pending = production._get_pending_component_pickings()
            if pending:
                raise UserError(_(
                    "Tidak dapat melakukan produksi. Selesaikan seluruh "
                    "transfer komponen terlebih dahulu. (%(pickings)s)",
                    pickings=", ".join(pending.mapped("display_name")),
                ))
        return super().button_mark_done()