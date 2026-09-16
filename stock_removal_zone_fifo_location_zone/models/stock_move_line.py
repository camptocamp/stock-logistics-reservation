# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _zone_in_date_to_propagate(self, location):
        source_zone = self.location_id.zone_location_id
        destination_zone = location.zone_location_id
        if not source_zone and not destination_zone:
            # No location flagged as a zone around either side, so keep the
            # zones defined by the removal strategy of an ancestor location.
            return super()._zone_in_date_to_propagate(location)
        # Replaces that definition with the one of stock_location_zone.
        return self._zone_in_date_between(source_zone, destination_zone)
