# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_project_tracking = fields.Selection(
        selection=[
            ('no', 'Nothing'),
            ('task', 'Task'),
            ('project_task', 'Project & Task'),
            ('project', 'Project'),
        ],
        string="Create Project on Order", default="no", copy=False,
        help="On Sales Order confirmation, a Storable product can generate a project and/or "
             "tasks while keeping the standard Inventory flow.\n"
             "'Task': create a task in the project set on this product.\n"
             "'Project & Task': create one project for the Sales Order and one task per order line.\n"
             "'Project': create one project for the Sales Order without tasks.",
    )
    stock_project_id = fields.Many2one(
        'project.project', string="Stock Project", company_dependent=True, copy=False,
        help="Project in which tasks of this product will be created on Sales Order "
             "confirmation (mode 'Task'). Values are company-specific.",
    )

    @api.onchange('detailed_type')
    def _onchange_detailed_type_stock_project(self):
        if self.detailed_type != 'product':
            self.stock_project_tracking = 'no'
            self.stock_project_id = False

    @api.onchange('stock_project_tracking')
    def _onchange_stock_project_tracking(self):
        if self.stock_project_tracking != 'task':
            self.stock_project_id = False

    def write(self, vals):
        if vals.get('detailed_type') and vals['detailed_type'] != 'product':
            vals = dict(vals, stock_project_tracking='no', stock_project_id=False)
        return super().write(vals)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    stock_project_tracking = fields.Selection(related='product_tmpl_id.stock_project_tracking')
    stock_project_id = fields.Many2one(related='product_tmpl_id.stock_project_id', readonly=False)