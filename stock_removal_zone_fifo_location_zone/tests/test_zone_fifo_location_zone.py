# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.stock_removal_zone_fifo.tests.common import ZoneFifoCommon


class TestZoneFifoLocationZone(ZoneFifoCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        (cls.zone_a | cls.zone_b).write({"is_zone": True})

    def test_unflagged_locations_keep_the_strategy_zones(self):
        """Flagging no zone at all must not disable Zone-Level FIFO."""
        (self.zone_a | self.zone_b).write({"is_zone": False})
        self._make_quant(
            self.bin_a1,
            10,
            in_date="2026-01-01 08:00:00",
            zone_in_date="2026-02-01 08:00:00",
        )
        self._move(self.bin_a1, self.bin_a2, 10)
        self.assertEqual(
            self._quant(self.bin_a2).zone_in_date, self._dt("2026-02-01 08:00:00")
        )

    def test_zones_are_wired(self):
        self.assertEqual(self.bin_a1.zone_location_id, self.zone_a)
        self.assertEqual(self.bin_a2.zone_location_id, self.zone_a)
        self.assertEqual(self.bin_b1.zone_location_id, self.zone_b)
        self.assertFalse(self.loc_outside.zone_location_id)

    def test_move_inside_a_zone_keeps_the_date(self):
        self._make_quant(
            self.bin_a1,
            10,
            in_date="2026-01-01 08:00:00",
            zone_in_date="2026-02-01 08:00:00",
        )
        self._move(self.bin_a1, self.bin_a2, 10)
        self.assertEqual(
            self._quant(self.bin_a2).zone_in_date, self._dt("2026-02-01 08:00:00")
        )

    def test_move_to_another_zone_resets_the_date(self):
        self._make_quant(
            self.bin_a1,
            10,
            in_date="2026-01-01 08:00:00",
            zone_in_date="2026-02-01 08:00:00",
        )
        before = fields.Datetime.now()
        self._move(self.bin_a1, self.bin_b1, 10)
        self.assertGreaterEqual(self._quant(self.bin_b1).zone_in_date, before)

    def test_move_from_outside_into_a_zone_resets_the_date(self):
        self._make_quant(
            self.loc_outside,
            10,
            in_date="2026-01-01 08:00:00",
            zone_in_date="2026-02-01 08:00:00",
        )
        before = fields.Datetime.now()
        self._move(self.loc_outside, self.bin_a1, 10)
        self.assertGreaterEqual(self._quant(self.bin_a1).zone_in_date, before)

    def test_merge_into_existing_stock_keeps_the_oldest_date(self):
        """Oldest wins, as the core does for in_date."""
        self._make_quant(
            self.bin_a1,
            10,
            in_date="2026-01-01 08:00:00",
            zone_in_date="2026-02-01 08:00:00",
        )
        self._make_quant(
            self.bin_a2,
            5,
            in_date="2026-05-01 08:00:00",
            zone_in_date="2026-05-01 08:00:00",
        )
        self._move(self.bin_a1, self.bin_a2, 10)
        self.assertEqual(
            self._quant(self.bin_a2).zone_in_date, self._dt("2026-02-01 08:00:00")
        )

    def test_untracked_stock_of_the_destination_is_left_alone(self):
        """A tracked line must not restamp the untracked quant of the bin,
        which a lookup by location alone also returns."""
        self.product.tracking = "lot"
        lot = self.env["stock.lot"].create(
            {"name": "LOT-A1", "product_id": self.product.id}
        )
        Quant = self.env["stock.quant"]
        untracked = Quant.create(
            {
                "product_id": self.product.id,
                "location_id": self.bin_a2.id,
                "quantity": 5,
                "in_date": "2026-09-01 08:00:00",
                "zone_in_date": "2026-09-01 08:00:00",
            }
        )
        Quant.create(
            {
                "product_id": self.product.id,
                "location_id": self.bin_a1.id,
                "lot_id": lot.id,
                "quantity": 10,
                "in_date": "2026-02-01 08:00:00",
                "zone_in_date": "2026-02-01 08:00:00",
            }
        )
        self._move(self.bin_a1, self.bin_a2, 10)
        self.assertEqual(untracked.zone_in_date, self._dt("2026-09-01 08:00:00"))
        moved = self._quant(self.bin_a2).filtered("lot_id")
        self.assertEqual(moved.zone_in_date, self._dt("2026-02-01 08:00:00"))

    def test_replenished_pallet_is_picked_last(self):
        """A2 was received before A1 but only just brought into the zone.
        Standard FIFO would pick A2; Zone-Level FIFO picks A1."""
        self._make_quant(
            self.bin_a1,
            10,
            in_date="2026-03-01 08:00:00",
            zone_in_date="2026-03-01 08:00:00",
        )
        reserve = self._make_quant(self.loc_outside, 10, in_date="2026-01-01 08:00:00")
        self._move(self.loc_outside, self.bin_a2, 10)
        self.assertFalse(reserve.exists() and reserve.quantity)

        move = self._move(self.stock_loc, self.customer_loc, 10, done=False)
        self.assertEqual(move.move_line_ids.location_id, self.bin_a1)
        # The replenished pallet still carries the old incoming date, so plain
        # FIFO would have picked it first.
        self.assertEqual(
            self._quant(self.bin_a2).in_date, self._dt("2026-01-01 08:00:00")
        )
