from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from requests import request
import base64

class SaleOrder(models.Model):
    _inherit = "sale.order"

    sendcloud_shipping_location_ids = fields.One2many("sendcloud.locations", "sale_order_id", string="Sendcloud Locations")
    sendcloud_shipping_location_id = fields.Many2one("sendcloud.locations", string="Sendcloud Locations",help="Sendcloud locations",copy=False)
    sendcloud_service_id = fields.Many2one('sendcloud.shipping.services', string="Sendcloud Service")
    
    def get_locations(self):
        order = self
        # Shipper and Recipient Address
        shipper_address = order.warehouse_id.partner_id
        recipient_address = order.partner_shipping_id
        # check sender Address
        if not shipper_address.zip or not shipper_address.city or not shipper_address.country_id:
            raise ValidationError("Please Define Proper Sender Address!")
        # check Receiver Address
        if not recipient_address.zip or not recipient_address.city or not recipient_address.country_id:
            raise ValidationError("Please Define Proper Recipient Address!")
        if not self.carrier_id.company_id:
            raise ValidationError("Credential not available!")
        try:
            try:
                data = "%s:%s" % (
                self.carrier_id.company_id.sendcloud_api_key, self.carrier_id.company_id.sendcloud_api_secret)
                encode_data = base64.b64encode(data.encode("utf-8"))
                authrization_data = "Basic %s" % (encode_data.decode("utf-8"))
                url = "https://servicepoints.sendcloud.sc/api/v2/servicepoints/?country=%s&postalCode=%s&language=en&city=%s" % (
                recipient_address.country_id and recipient_address.country_id.code or "",recipient_address.zip,recipient_address.city)
                headers = {"Authorization": "%s" % authrization_data}
                response_data = request(method='GET', url=url, headers=headers)
            except Exception as e:
                raise ValidationError(e)
            if response_data.status_code in [200, 201]:
                response_data = response_data.json()
                sendcloud_locations = self.env['sendcloud.locations']
                existing_records = self.env['sendcloud.locations'].search(
                    [('sale_order_id', '=', order and order.id)])
                existing_records.sudo().unlink()
                if response_data:
                    if isinstance(response_data,dict):
                        response_data = [response_data]
                    for location in response_data:
                        send_cloud_location_id = location.get('id')
                        name = location.get('name')
                        city = location.get('city')
                        zip = location.get('postal_code')
                        street = location.get('street')
                        country_id = self.env['res.country'].search([('code', '=', location.get('country'))], limit=1)
                        send_cloud_location_code = location.get('code')
                        send_cloud_carrier = location.get('carrier')
                        sale_order_id = self.id
                        send_cloud_location_id = sendcloud_locations.sudo().create(
                        {'name': "%s" % (name),
                         'city': "%s" % (city),
                         'send_cloud_location_id':send_cloud_location_id,
                         'zip':zip,
                         'street':street,
                         'country_id':country_id and country_id.id,
                         'send_cloud_location_code':send_cloud_location_code,
                         'send_cloud_carrier':send_cloud_carrier,
                         'sale_order_id':sale_order_id})
                else:
                    raise ValidationError("Location Not Found For This Address! %s "% (response_data))
            else:
                raise ValidationError("%s %s" % (response_data, response_data.text))
        except Exception as e:
            raise ValidationError(e)
