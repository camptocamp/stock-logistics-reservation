# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import Command, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def write(self, vals):
        skip_update_carrier_routes = self.env.context.get("skip_update_carrier_routes")
        if vals.get("carrier_id") and not skip_update_carrier_routes:
            # Update stock rules on moves when carrier is changed on transfers
            # not yet released.
            # This is only needed for Odoo 17.0+, allowing to set routes on carriers.
            orig_carriers = {rec: rec.carrier_id for rec in self}
            res = super().write(vals)
            pickings_updated_ids = []
            for picking in self:
                # Skip if carrier didn't changed
                if picking.carrier_id != orig_carriers[picking]:
                    pickings_updated_ids.append(picking.id)
            pickings_updated = self.browse(pickings_updated_ids)
            for picking in pickings_updated:
                picking._update_moves_with_carrier_routes()
            return res
        return super().write(vals)

    def _update_moves_with_carrier_routes(self):
        """Update stock rules on transfer's moves based on new carrier's routes."""
        self.ensure_one()
        # Skip if transfer is already released
        if not self.need_release:
            return self.env["stock.move"]
        # Set a context key to not trigger a carrier change on the
        # procurement group
        defaults = {
            "carrier_id": self.carrier_id.id,
            "name": self.env._(
                "%s - Alternative carrier %s", self.group_id.name, self.carrier_id.name
            ),
        }
        self.group_id = self.group_id.copy(default=defaults)
        active_moves = self.move_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        active_moves.group_id = self.group_id
        # Manage the carrier route
        if (
            (rerouted_moves := active_moves.filtered(lambda m: not m.route_ids))
            and (routes := self.carrier_id.route_ids.filtered("active"))
            and (
                rule := self.env["procurement.group"]._get_rule(
                    self.env["product.product"],
                    self.location_dest_id,
                    {"route_ids": routes},
                )
            )
        ):
            rerouted_moves.write(
                {
                    "location_id": rule.location_src_id.id,
                    "rule_id": rule.id,
                    "route_ids": [Command.link(rule.route_id.id)],
                    "picking_type_id": rule.picking_type_id.id,
                    "procure_method": rule.procure_method,
                    "propagate_cancel": rule.propagate_cancel,
                }
            )
            return rerouted_moves
        return self.env["stock.move"]
