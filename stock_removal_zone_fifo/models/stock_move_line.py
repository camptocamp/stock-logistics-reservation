# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _synchronize_quant(
        self, quantity, location, action="available", in_date=False, **quants_value
    ):
        # A positive available quantity is the leg putting the goods down. Read
        # the date stored there first, as the leg may create the quant.
        put_down = action == "available" and quantity > 0
        previous_dates = (
            self._zone_quants(location, **quants_value).mapped("zone_in_date")
            if put_down
            else []
        )
        res = super()._synchronize_quant(
            quantity, location, action=action, in_date=in_date, **quants_value
        )
        if put_down:
            self._apply_zone_in_date(location, previous_dates, **quants_value)
        return res

    def _apply_zone_in_date(self, location, previous_dates, **quants_value):
        self.ensure_one()
        zone_in_date = self._zone_in_date_to_propagate(location)
        if not zone_in_date:
            return
        # Oldest wins, as the core does for in_date: arriving goods never push
        # the ones already there back in the queue.
        zone_in_date = min([zone_in_date] + previous_dates)
        self._zone_quants(location, **quants_value).zone_in_date = zone_in_date

    def _zone_in_date_to_propagate(self, location):
        """Hook: zone entry date the goods get in ``location``, or False to keep
        the one the core propagated. See the DEVELOP section of the README."""
        return False

    def _source_zone_in_date(self):
        """Zone entry date of the quant the goods were taken from. Still
        readable here: emptied quants are dropped at the end of _action_done."""
        self.ensure_one()
        dates = self._zone_quants(
            self.location_id, lot=self.lot_id, package=self.package_id
        ).mapped("zone_in_date")
        return min(dates) if dates else False

    def _zone_quants(self, location, **quants_value):
        self.ensure_one()
        # Used twice below, unlike package and owner.
        lot = quants_value.get("lot", self.lot_id)
        quants = (
            self.env["stock.quant"]
            .sudo()
            ._gather(
                self.product_id,
                location,
                lot_id=lot,
                package_id=quants_value.get("package", self.package_id),
                owner_id=quants_value.get("owner", self.owner_id),
                strict=True,
            )
        )
        if lot:
            # _gather also returns the untracked quant of the location, which
            # holds other goods than the ones this line moves.
            quants = quants.filtered(lambda quant: quant.lot_id)
        return quants
