# -*- coding: utf-8 -*-
from odoo import _, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    landed_cost_count = fields.Integer(
        "Landed Cost Count", compute="_compute_landed_cost_count")

    def _compute_landed_cost_count(self):
        LandedCost = self.env["stock.landed.cost"].sudo()
        for production in self:
            production.landed_cost_count = LandedCost.search_count(
                [("mrp_production_ids", "in", production.ids)])

    def action_add_landed_cost(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Add Cost"),
            "res_model": "stock.landed.cost",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_target_model": "manufacturing",
                "default_mrp_production_ids": [(6, 0, [self.id])],
                "default_company_id": self.company_id.id,
                "default_description": _("Additional manufacturing cost for %s") % self.display_name,
            },
        }

    def action_view_landed_costs(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_landed_costs.action_stock_landed_cost")
        action["domain"] = [("mrp_production_ids", "in", self.ids)]
        action["context"] = {
            "default_target_model": "manufacturing",
            "default_mrp_production_ids": [(6, 0, [self.id])],
        }
        return action