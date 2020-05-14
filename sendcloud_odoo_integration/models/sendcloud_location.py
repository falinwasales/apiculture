from odoo import models, fields, api


class SendcloudLocations(models.Model):
    _name = "sendcloud.locations"

    name = fields.Char(string="Sendcloud Service Point Name", help="Sendcloud Service Point Name")
    city = fields.Char(string="Sendcloud City", help="Sendcloud city")
    zip = fields.Char(string="Sendcloud Zip", help="Sendcloud zip")
    street = fields.Char(string="Sendcloud Street", help="Sendcloud street")
    country_id = fields.Char(string="Sendcloud Country ID", help="Sendcloud Country ID")
    state_id = fields.Char(string="Sendcloud State ID", help="Sendcloud State ID")
    send_cloud_location_id = fields.Char(string="Sendcloud Location ID", help="Sendcloud Location ID")
    send_cloud_location_code = fields.Char(string="Sendcloud Location Code", help="Sendcloud Location Code")
    send_cloud_carrier = fields.Char(string="Sendcloud Carrier Code", help="Sendcloud Carrier Code")
    sale_order_id = fields.Many2one("sale.order", string="Sales Order")

    def set_location(self):
        self.ensure_one()
        self.sale_order_id.sendcloud_shipping_location_id = self.id
