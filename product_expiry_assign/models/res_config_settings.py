# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ignore_expiration_date = fields.Boolean(
        config_parameter="product_expiry_assign.ignore_expiration_date",
    )
