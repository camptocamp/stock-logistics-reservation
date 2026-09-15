# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _zone_in_date_to_propagate(self, location):
        destination_zone = location.zone_location_id
        if not destination_zone:
            # Outside any zone, nothing to track.
            return super()._zone_in_date_to_propagate(location)
        if destination_zone == self.location_id.zone_location_id:
            # Same zone: the goods were already in it, keep their date so an
            # internal reorganisation does not requeue them.
            return self._source_zone_in_date()
        # Another zone: the goods arrive in it now, whatever in_date says.
        return fields.Datetime.now()
