# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _carrier_can_be_changed(self):
        self.ensure_one()
        active_moves = self.move_ids.filtered(
            lambda move: move.state not in ("done", "cancel")
        )
        if not active_moves:
            return False
        for move in active_moves:
            if not move.need_release:
                return False
        return True

    def _apply_alternative_carrier(self):
        if not self._carrier_can_be_changed():
            return False
        carrier = self._get_preferred_carrier()
        if not carrier:
            return False
        if carrier == self.carrier_id:
            return False
        # Set a context key to not trigger a carrier change on the
        # procurement group
        self.with_context(skip_align_group_carrier=True).carrier_id = carrier
        self.group_id = self.group_id.copy(default={"carrier_id": carrier.id})
        return True

    def _get_preferred_carrier(self):
        self.ensure_one()
        picking_carrier = self.carrier_id
        # @jbaudoux suggested to drop picking_carrier from this check,
        # but I disagree because current carrier could be the best match,
        # and I guess we do not want to force another carrier in such case.
        # see https://github.com/OCA/stock-logistics-reservation/pull/17#discussion_r2215062326
        possible_carriers = picking_carrier | picking_carrier.alternative_carrier_ids
        for carrier in possible_carriers.sorted("sequence"):
            if carrier._match_picking(self):
                return carrier
