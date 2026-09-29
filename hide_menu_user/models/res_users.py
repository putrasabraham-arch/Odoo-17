# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models, api, _
from odoo.http import request
import hashlib
import json
from odoo.tools import ustr


class HideMenuRule(models.Model):
    """
    Per-company menu restriction rule for a specific user.
    Each rule hides the selected menus only when the given company
    is active (checked in the company switcher).
    """
    _name = 'hide.menu.rule'
    _description = 'Hide Menu Rule (per company)'
    _rec_name = 'company_id'

    user_id = fields.Many2one(
        'res.users', string="User", required=True, ondelete='cascade',
        index=True)
    company_id = fields.Many2one(
        'res.company', string="Company", required=True, ondelete='cascade',
        index=True, help='Menus will be hidden for this user only when '
                         'this company is active.')
    menu_ids = fields.Many2many(
        'ir.ui.menu', 'hide_menu_rule_menu_rel', 'rule_id', 'menu_id',
        string="Hidden Menu", help='Menu items hidden for this user when '
                                   'this company is active.')

    _sql_constraints = [
        ('user_company_uniq', 'unique(user_id, company_id)',
         'Only one hidden-menu rule per user per company is allowed.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        rules = super().create(vals_list)
        # menu data is cached per user: invalidate it so the new rules apply
        rules.env.registry.clear_cache()
        return rules

    def write(self, vals):
        res = super().write(vals)
        self.env.registry.clear_cache()
        return res

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_cache()
        return res


class ResUsers(models.Model):
    """
    Model to handle hiding specific menu items for certain users.
    `hide_menu_ids` applies to ALL companies (legacy/global behaviour),
    while `hide_menu_rule_ids` allows a different set of hidden menus
    per company.
    """
    _inherit = 'res.users'

    hide_menu_ids = fields.Many2many(
        'ir.ui.menu', string="Hidden Menu (All Companies)",
        store=True, help='Select menu items that need to be hidden to this '
                         'user in every company.')
    hide_menu_rule_ids = fields.One2many(
        'hide.menu.rule', 'user_id', string="Hidden Menu per Company",
        copy=False, help='Company-specific hidden menus. Applies only when '
                         'the corresponding company is active.')
    is_admin = fields.Boolean(compute='_get_is_admin', string="Is Admin",
                              help='Check if the user is an admin.')

    def _get_is_admin(self):
        """
        Compute method to check if the user is an admin.
        The Hide specific menu tab will be hidden for the Admin user form.
        """
        for rec in self:
            rec.is_admin = False
            if rec.id == self.env.ref('base.user_admin').id:
                rec.is_admin = True

    def write(self, vals):
        res = super().write(vals)
        if 'hide_menu_ids' in vals or 'hide_menu_rule_ids' in vals:
            self.env.registry.clear_cache()
        return res

    def _get_active_company_ids(self):
        """Companies currently active in the webclient (company switcher).

        The webclient stores the active companies in the `cids` cookie and
        does NOT send `allowed_company_ids` in the context of the menu
        loading request, so we read the cookie as a fallback. If no cookie
        is available (first load / non-webclient context), fall back on the
        user main company, matching the webclient behaviour
        (see `computeActiveCompanyIds` in company_service.js).
        """
        self.ensure_one()
        company_ids = self.env.context.get('allowed_company_ids')
        if company_ids:
            return list(company_ids)
        if request:
            raw_cids = request.httprequest.cookies.get('cids')
            if raw_cids:
                try:
                    # separators: '-' (17.0) and legacy ','
                    return [
                        int(part) for part in raw_cids.replace('-', ',').split(',')
                        if part
                    ]
                except ValueError:
                    pass
        return self.company_id.ids

    def _get_all_hidden_menus(self):
        """Menus hidden for this user in the companies currently active
        (company switcher), plus the global ones (All Companies)."""
        self.ensure_one()
        menus = self.hide_menu_ids
        rules = self.env['hide.menu.rule'].sudo().search([
            ('user_id', '=', self.id),
            ('company_id', 'in', self._get_active_company_ids()),
        ])
        menus |= rules.menu_ids
        return menus


class IrUiMenu(models.Model):
    """
    Model to restrict the menu for specific users.
    """
    _inherit = 'ir.ui.menu'

    restrict_user_ids = fields.Many2many(
        'res.users', string="Restricted Users",
        compute='_compute_restrict_user_ids',
        help='Users restricted from accessing this menu in any company.')

    @api.depends()
    def _compute_restrict_user_ids(self):
        """Users having this menu hidden in at least one company."""
        rules = self.env['hide.menu.rule'].sudo().search([])
        for menu in self:
            menu.restrict_user_ids = rules.filtered(
                lambda rule: menu in rule.menu_ids).user_id

    def _get_global_hidden_menu_ids(self):
        """Ids of the menus hidden GLOBALLY (All Companies) for the current
        user. Company-independent on purpose: this is used inside
        `load_menus()` whose result is cached per user, so it must never
        depend on the active companies. Per-company filtering is done in
        `load_web_menus()` instead (see below)."""
        if self.env.user.has_group('base.group_system'):
            return None
        global_menus = self.env.user.hide_menu_ids
        return set(global_menus.ids) if global_menus else None

    def _get_hidden_menu_ids(self):
        """Ids of the menus hidden for the current user in the active
        companies (None means nothing is hidden)."""
        if self.env.user.has_group('base.group_system'):
            return None
        hidden = self.env.user._get_all_hidden_menus()
        return set(hidden.ids) if hidden else None

    def _prune_hidden_web_menus(self, web_menus, hidden_ids):
        """Remove hidden menus (and their whole subtree) from the
        webclient menu dict, in place."""
        to_remove = set()

        def _collect(menu_id):
            if menu_id in to_remove:
                return
            to_remove.add(menu_id)
            for child in web_menus.get(menu_id, {}).get('children', []):
                _collect(child)

        def _prune(menu_id):
            entry = web_menus.get(menu_id)
            if not entry:
                return
            kept = []
            for child in entry['children']:
                if child in hidden_ids:
                    _collect(child)
                else:
                    kept.append(child)
                    _prune(child)
            entry['children'] = kept

        _prune('root')
        for menu_id in to_remove:
            web_menus.pop(menu_id, None)
        return web_menus

    def load_web_menus(self, debug):
        """Override to filter out per-company hidden menus.

        `load_menus()` is cached per user and does not depend on the active
        companies, so the per-company filtering is applied here instead:
        `load_web_menus` runs on every webclient load and therefore always
        reflects the companies currently active in the switcher.
        """
        web_menus = super(IrUiMenu, self).load_web_menus(debug)
        hidden_ids = self._get_hidden_menu_ids()
        if hidden_ids:
            self._prune_hidden_web_menus(web_menus, hidden_ids)
        return web_menus

    @api.returns('self')
    def _filter_visible_menus(self):
        """
        Override to filter out menus hidden GLOBALLY (All Companies) for the
        current user.

        IMPORTANT: only company-independent restrictions may be applied
        here. This method runs inside `load_menus()`, whose result is
        cached per user regardless of the active companies - applying
        per-company rules here would freeze the first computed company
        combination into the cached menu tree. Per-company filtering is
        handled in `load_web_menus()` which runs on every webclient load.
        """
        menus = super(IrUiMenu, self)._filter_visible_menus()

        hidden_ids = self._get_global_hidden_menu_ids()
        if not hidden_ids:
            return menus

        # Hide restricted menus and every descendant of a hidden menu
        parent_by_menu = {menu.id: menu.parent_id for menu in menus}

        def _is_hidden(menu):
            current = menu
            while current:
                if current.id in hidden_ids:
                    return True
                current = parent_by_menu.get(current.id)
            return False

        return menus.filtered(lambda m: not _is_hidden(m))


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        cache_hashes = result.get('cache_hashes') or {}
        if 'load_menus' in cache_hashes:
            # Recompute the load_menus cache hash from the menus actually
            # served (filtered per user AND per active companies). The
            # webclient uses this hash in the `/web/webclient/load_menus/<hash>`
            # URL which the browser caches for up to a year
            # (Cache-Control: public, max-age=STATIC_CACHE_LONG). Baking the
            # filtered result into the hash guarantees a fresh fetch whenever
            # the hidden menus or the active companies change.
            menus = request.env['ir.ui.menu'].with_context(
                lang=request.session.context.get('lang'),
            ).load_web_menus(request.session.debug)
            ordered_menus = {str(k): v for k, v in menus.items()}
            menu_json = json.dumps(ordered_menus, default=ustr, sort_keys=True).encode()
            cache_hashes['load_menus'] = hashlib.sha512(menu_json).hexdigest()[:64]
        return result