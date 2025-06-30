# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.osv.expression import AND
from odoo.tools.safe_eval import const_eval


class StockPicking(models.Model):
    _inherit = "stock.picking"


    def _carrier_can_be_changed(self):
        self.ensure_one()
        active_moves = self.move_ids.filtered(
            lambda move: move.state not in ("done", "cancel")
        )
        if active_moves:
            for move in active_moves:
                if not move.need_release:
                    return False
            return True


    def check_alternative_carriers(self):
        if not self._carrier_can_be_changed():
            return
        carrier = self.get_preferred_carrier()
        if not carrier:
            return {
                "warning": {
                    "title": _("Cannot find preferred carrier"),
                    "message": _(
                        "No preferred carrier could be found "
                        "automatically for this delivery order. Please"
                        "select one manually."
                    ),
                }
            }
        # Set a context key to not trigger a carrier change on the
        # procurement group
        self.with_context(skip_align_group_carrier=True).carrier_id = carrier

    def get_preferred_carrier(self):
        self.ensure_one()
        picking_carrier = self.carrier_id
        alternative_carriers = picking_carrier | picking_carrier.alternative_carrier_ids
        for carrier in alternative_carriers.sorted("sequence"):
            if carrier._match_picking(self):
                return carrier
