# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    # The column was just filled with the install date by the field default.
    # The incoming date is the best guess of when the goods entered their zone.
    env.cr.execute("UPDATE stock_quant SET zone_in_date = in_date")
    _logger.info("Initialized zone_in_date on %s quants", env.cr.rowcount)
