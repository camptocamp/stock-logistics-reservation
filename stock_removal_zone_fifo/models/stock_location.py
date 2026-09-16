# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    @api.model
    def _zone_removal_strategies(self):
        # Extended by the modules adding another zone-based strategy.
        return ["zone_fifo"]

    def _get_zone_location(self):
        """Nearest ancestor, self included, whose removal strategy defines a
        zone. Empty when no ancestor carries one."""
        self.ensure_one()
        methods = self._zone_removal_strategies()
        location = self.sudo()
        while location:
            if location.removal_strategy_id.method in methods:
                return location
            location = location.location_id
        return self.browse()
