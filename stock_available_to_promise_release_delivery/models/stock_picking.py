# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import Command, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def write(self, vals):
        if vals.get("carrier_id"):
            # Update stock rules on moves when carrier is changed on transfers
            # not yet released.
            # This is only needed for Odoo 17.0+, allowing to set routes on carriers.
            orig_carriers = {rec: rec.carrier_id for rec in self}
            res = super().write(vals)
            pickings_updated_ids = []
            for picking in self:
                # Skip assigned pickings
                if picking.state in ("assigned", "partially_available"):
                    continue
                # Skip if carrier didn't changed
                if picking.carrier_id != orig_carriers[picking]:
                    pickings_updated_ids.append(picking.id)
            pickings_updated = self.browse(pickings_updated_ids)
            pickings_updated._sync_moves_with_carrier_routes()
            return res
        return super().write(vals)

    def _sync_moves_with_carrier_routes(self):
        """Update stock rules on transfer's moves based on new carrier's routes."""
        for picking in self:
            # Skip if transfer is already released
            if not picking.need_release:
                continue
            # Skip if no route is set on the new carrier
            routes = picking.carrier_id.route_ids.filtered("active")
            if not routes:
                continue
            rule = self.env["procurement.group"]._get_rule(
                self.env["product.product"],
                self.location_dest_id,
                {"route_ids": routes},
            )
            if not rule:
                # FIXME raise an error if no rule can be found for that carrier route?
                continue
            picking.move_ids.write(
                {
                    "location_id": rule.location_src_id.id,
                    "rule_id": rule.id,
                    "route_ids": [Command.link(rule.route_id.id)],
                    "picking_type_id": rule.picking_type_id.id,
                    "procure_method": rule.procure_method,
                    "propagate_cancel": rule.propagate_cancel,
                }
            )
