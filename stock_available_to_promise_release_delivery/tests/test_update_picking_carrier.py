# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
from .common import Common


class TestUpdateCarrierRoute(Common):
    def test_update_carrier_route(self):
        """Switch from one carrier to another and check routing."""
        ship = self._create_picking_chain(self.wh, [(self.product1, 5)])
        self.assertTrue(ship.need_release)
        self.assertFalse(ship.carrier_id)
        self.assertTrue(ship.move_ids.rule_id)
        self.assertFalse(ship.move_ids.route_ids)
        # Set a carrier without route: no change expected
        ship.carrier_id = self.normal_carrier
        self.assertEqual(ship.carrier_id, self.normal_carrier)
        self.assertTrue(current_rule := ship.move_ids.rule_id)
        self.assertFalse(forced_route := ship.move_ids.route_ids)
        # Set a carrier with a route compatible with dest location (Customers)
        # => moves are rerouted
        ship.carrier_id = self.the_poste_carrier
        self.assertEqual(ship.carrier_id, self.the_poste_carrier)
        self.assertTrue(current_rule := ship.move_ids.rule_id)
        self.assertTrue(forced_route := ship.move_ids.route_ids)
        self.assertEqual(current_rule, self.the_poste_delivery_rule)
        self.assertEqual(forced_route, self.the_poste_carrier.route_ids)
        # Reset to carrier without route: no change regarding routing
        ship.carrier_id = self.normal_carrier
        self.assertEqual(ship.carrier_id, self.normal_carrier)
        self.assertTrue(current_rule := ship.move_ids.rule_id)
        self.assertTrue(forced_route := ship.move_ids.route_ids)
        self.assertEqual(current_rule, self.the_poste_delivery_rule)
        self.assertEqual(forced_route, self.the_poste_carrier.route_ids)

    def test_release_carrier_route(self):
        """Release/unrelease a delivery order with a new carrier."""
        ship = self._create_picking_chain(self.wh, [(self.product1, 5)])
        self._update_qty_in_location(self.wh.lot_stock_id, self.product1, 5)
        self.assertTrue(ship.need_release)
        self.assertTrue(ship.release_ready)
        # When releasing, the ship will take the usual WH delivery route
        ship.release_available_to_promise()
        pick = ship.move_ids.move_orig_ids.picking_id
        self.assertTrue(pick)
        self.assertEqual(pick.move_ids.rule_id, self.wh.delivery_route_id.rule_ids[0])
        self.assertEqual(
            pick.picking_type_id, self.wh.delivery_route_id.rule_ids[0].picking_type_id
        )
        # Unrelease, switch to carrier w/ route and release: taking the new route
        ship.unrelease()
        ship.carrier_id = self.the_poste_carrier
        self.assertEqual(ship.move_ids.rule_id, self.the_poste_delivery_rule)
        ship.release_available_to_promise()
        pick = ship.move_ids.move_orig_ids.picking_id
        self.assertTrue(pick)
        self.assertEqual(pick.move_ids.rule_id, self.the_poste_pick_rule)
        self.assertEqual(pick.picking_type_id, self.the_poste_pick_rule.picking_type_id)
        # Unrelease, switch to carrier w/o route and release: still using the new route
        ship.unrelease()
        ship.carrier_id = self.normal_carrier
        self.assertEqual(ship.move_ids.rule_id, self.the_poste_delivery_rule)
        ship.release_available_to_promise()
        pick = ship.move_ids.move_orig_ids.picking_id
        self.assertTrue(pick)
        self.assertEqual(pick.move_ids.rule_id, self.the_poste_pick_rule)
        self.assertEqual(pick.picking_type_id, self.the_poste_pick_rule.picking_type_id)
