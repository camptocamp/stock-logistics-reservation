# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _is_zone_changed(self, location):
        source_zone = self.location_id.zone_location_id
        destination_zone = location.zone_location_id
        if not source_zone and not destination_zone:
            # no location flagged as a zone on either side, so keep the zones
            # defined by the removal strategy of an ancestor location
            return super()._is_zone_changed(location)
        return location._compare_zones(source_zone, destination_zone)
