# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_estimated_shipping_quantity(self):
        self.ensure_one()
        # use available promised qty to estimate the shipping weight
        return self.ordered_available_to_promise_uom_qty

    def _get_new_picking_values(self):
        vals = super()._get_new_picking_values()
        # Take the carrier_id from the group only when we have a related line
        # (i.e. we are in an OUT). It reflects the code of the super method in
        # "delivery" which takes the carrier of the related SO through SO line
        if self.sale_line_id:
            group_carrier = self.mapped("group_id.carrier_id")
            if group_carrier:
                vals["carrier_id"] = group_carrier.id
        return vals


    def _before_release(self):
        # if self doesn't match the moves of the related pickings,
        # extract them in a backorder
        with self.env.cr.savepoint() as savepoint:
            picking = self.picking_id
            if self != picking.move_ids:
                self._unreleased_to_backorder()
                picking = self.picking_id
            # If a better picking is found, assign it, otherwise rollback
            carrier_before = picking.carrier_id
            picking.check_alternative_carriers()
            if carrier_before == picking.carrier_id:
                savepoint.rollback()
            else:
                picking.group_id = picking.group_id.copy(
                    default={"carrier_id": picking.carrier_id.id}
                )
