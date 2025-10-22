# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ignore_expiration_date = fields.Boolean(
        related="company_id.ignore_expiration_date", readonly=False
    )
