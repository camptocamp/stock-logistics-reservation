# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Available to Promise Release - Carrier Alternative",
    "summary": "Advanced selection of preferred shipping methods",
    "version": "18.0.1.0.0",
    "category": "Operations/Inventory/Delivery",
    "website": "https://github.com/OCA/wms",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "delivery_carrier_picking_valid_packaging_weight",
        "stock_available_to_promise_release",
        "stock_picking_group_by_partner_by_carrier",
    ],
    "data": [
        "views/stock_location_route.xml",
        "views/delivery_carrier.xml",
    ],
}
