# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import ZoneFifoCommon


class TestZoneFifo(ZoneFifoCommon):
    def test_removal_strategy_order(self):
        order = self.env["stock.quant"]._get_removal_strategy_order("zone_fifo")
        self.assertEqual(order, "zone_in_date ASC, in_date ASC, id")

    def test_other_strategies_untouched(self):
        Quant = self.env["stock.quant"]
        self.assertEqual(Quant._get_removal_strategy_order("fifo"), "in_date ASC, id")

    def test_zone_in_date_defaults_to_in_date(self):
        quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.bin_a1.id,
                "quantity": 10,
                "in_date": "2026-01-01 08:00:00",
            }
        )
        self.assertEqual(quant.zone_in_date, self._dt("2026-01-01 08:00:00"))

    def test_zone_in_date_is_never_empty(self):
        """No NULL to handle, so the ordering stays a plain ASC sort."""
        quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.bin_a1.id,
                "quantity": 10,
            }
        )
        self.assertTrue(quant.zone_in_date)

    def test_reservation_follows_zone_in_date(self):
        """A1 has the oldest incoming date, so standard FIFO would take it.
        A2 entered the zone first, so Zone-Level FIFO takes A2."""
        self._make_quant(
            self.bin_a1,
            10,
            in_date="2026-01-01 08:00:00",
            zone_in_date="2026-06-01 08:00:00",
        )
        self._make_quant(
            self.bin_a2,
            10,
            in_date="2026-03-01 08:00:00",
            zone_in_date="2026-02-01 08:00:00",
        )
        move = self._move(self.stock_loc, self.customer_loc, 10, done=False)
        self.assertEqual(move.move_line_ids.location_id, self.bin_a2)

    def test_reservation_falls_back_on_in_date(self):
        """Equal zone entry dates are broken by the incoming date."""
        same_day = "2026-06-01 08:00:00"
        self._make_quant(
            self.bin_a1, 10, in_date="2026-03-01 08:00:00", zone_in_date=same_day
        )
        self._make_quant(
            self.bin_a2, 10, in_date="2026-01-01 08:00:00", zone_in_date=same_day
        )
        move = self._move(self.stock_loc, self.customer_loc, 10, done=False)
        self.assertEqual(move.move_line_ids.location_id, self.bin_a2)

    def test_move_leaves_the_core_behaviour_alone(self):
        """Knowing no zone, it decides nothing on a move: zone_in_date keeps
        following in_date, so the strategy behaves like the standard FIFO."""
        self._make_quant(self.bin_a1, 10, in_date="2026-01-01 08:00:00")
        self._move(self.bin_a1, self.bin_a2, 10)
        quant = self._quant(self.bin_a2)
        self.assertEqual(quant.zone_in_date, self._dt("2026-01-01 08:00:00"))
        self.assertEqual(quant.zone_in_date, quant.in_date)

    def test_move_keeps_the_original_in_date(self):
        """in_date is still carried over, untouched."""
        self._make_quant(self.bin_a1, 10, in_date="2026-01-01 08:00:00")
        self._move(self.bin_a1, self.bin_a2, 10)
        self.assertEqual(
            self._quant(self.bin_a2).in_date, self._dt("2026-01-01 08:00:00")
        )

    def test_source_zone_in_date(self):
        """Reads the date of the quant the goods were taken from."""
        self._make_quant(
            self.bin_a1,
            10,
            in_date="2026-01-01 08:00:00",
            zone_in_date="2026-02-01 08:00:00",
        )
        # Not validated: once the move is done the emptied source quant is gone.
        move = self._move(self.bin_a1, self.bin_a2, 10, done=False)
        self.assertEqual(
            move.move_line_ids._source_zone_in_date(),
            self._dt("2026-02-01 08:00:00"),
        )
