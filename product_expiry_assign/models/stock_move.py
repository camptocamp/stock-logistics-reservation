# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def with_context(self, *args, **kwargs) -> api.Self:
        # Unset 'with_expiration' key if 'ignore_expiration_date' is set
        # NOTE: 'with_expiration' key is used in overrides of
        # _update_reserved_quantity and _get_available_quantity methods
        # in product_expiry module to later generate a domain skipping expired
        # quants during reservation in stock module.
        if (
            kwargs.get("ignore_expiration_date")
            or self.env.context.get("ignore_expiration_date")
        ) and "with_expiration" in kwargs:
            kwargs.pop("with_expiration")
        return super().with_context(*args, **kwargs)
