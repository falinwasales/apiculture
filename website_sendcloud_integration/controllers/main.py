from odoo import fields, http, tools, _
from odoo.http import request
import requests
import base64

class WebsiteSale(http.Controller):

    @http.route(['/sendcloud_service'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def sendcloud_service(self, **post):
        results = {}
        if post.get('order') and post.get('delivery_type'):
            delivery_method = request.env['delivery.carrier'].sudo().browse(int(post.get('delivery_type')))
            if delivery_method.delivery_type == 'sendcloud':
                location_required = True
                results = request.env['ir.ui.view'].render_template('website_sendcloud_integration.sendcloud_shipping_location', {'location_required': location_required})
        return results

    @http.route(['/get_location'], type='json', auth='public', methods=['POST'],
                website=True, csrf=False)
    def get_location(self, **post):
        order = request.website.sale_get_order()

        # Shipper and Recipient Address
        shipper_address = order.warehouse_id.partner_id
        recipient_address = order.partner_shipping_id
        # check sender Address
        if not shipper_address.zip or not shipper_address.city or not shipper_address.country_id:
            return {'error':'Please Define Proper Sender Address!'}
        # check Receiver Address
        if not recipient_address.zip or not recipient_address.city or not recipient_address.country_id:
            return {'error':'Please Define Proper Recipient Address!'}
        if not order.carrier_id.company_id:
            return {'error':'Credential not available!'}
        try:
            data = "%s:%s" % (
                order.carrier_id.company_id.sendcloud_api_key,
                order.carrier_id.company_id.sendcloud_api_secret)
            encode_data = base64.b64encode(data.encode("utf-8"))
            authrization_data = "Basic %s" % (encode_data.decode("utf-8"))
            carrier_code = order.carrier_id.sendcloud_service_id.sendcloud_carrier_name if order.carrier_id.sendcloud_service_id.sendcloud_carrier_name else "mondial_relay"
            url = "https://servicepoints.sendcloud.sc/api/v2/servicepoints/?carrier=%s&country=%s&postalCode=%s&language=en&city=%s" % (carrier_code,
                recipient_address.country_id and recipient_address.country_id.code or "",
                recipient_address.zip, recipient_address.city)
            headers = {"Authorization":"%s" % authrization_data}
            response_data = requests.get(url=url, headers=headers)
        except Exception as e:
            return {'error': e}
        if response_data.status_code in [200, 201]:
            response_data = response_data.json()
            sendcloud_locations = request.env['sendcloud.locations']
            existing_records = request.env['sendcloud.locations'].search(
                    [('sale_order_id', '=', order and order.id)])
            existing_records.sudo().unlink()
            if response_data:
                if isinstance(response_data, dict):
                    response_data = [response_data]
                dic = []
                count = 1
                for location in response_data:
                    send_cloud_location_id = location.get('id')
                    name = location.get('name')
                    city = location.get('city')
                    zip = location.get('postal_code')
                    street = location.get('street')
                    country_id = request.env['res.country'].sudo().search(
                            [('code', '=', location.get('country'))], limit=1)
                    send_cloud_location_code = location.get('code')
                    send_cloud_carrier = location.get('carrier')
                    sale_order_id = order and order.id
                    sendcloud_locations.sudo().create(
                            {'name':"%s" % (name),
                             'city':"%s" % (city),
                             'send_cloud_location_id':send_cloud_location_id,
                             'zip':zip,
                             'street':street,
                             'country_id':country_id and country_id.id,
                             'send_cloud_location_code':send_cloud_location_code,
                             'send_cloud_carrier':send_cloud_carrier,
                             'sale_order_id':sale_order_id})

                    latitude = float(location.get('latitude'))
                    longitude = float(location.get('longitude'))
                    count += count + 1
                    dic.append([name, latitude, longitude, count])
                print(dic)
                values = {
                    'locations': order.sendcloud_shipping_location_ids or []
                }
                tamplate = request.env['ir.ui.view'].render_template('website_sendcloud_integration.sendcloud_location_details', values)
                return {'template': tamplate, 'dic': dic}
            else:
                return {'error': "Location Not Found For This Address! %s " % (response_data)}
        else:
            return {'error': "%s %s" % (response_data, response_data.text)}

    @http.route(['/set_location'], type='json', auth='public', website=True, csrf=False)
    def set_location(self, location=False, **post):
        location_id = request.env['sendcloud.locations'].browse(location)
        if location_id and location_id.id:
            location_id.sale_order_id.sendcloud_shipping_location_id = location_id.id
            return {'success': True, 'name': location_id.name, 'city': location_id.city,
                    'zip': location_id.zip, 'street': location_id.street}

    @http.route(['/remove_location'], type='json', auth='public', website=True, csrf=False)
    def remove_location(self, location=False, **post):
        location_id = request.env['sendcloud.locations'].browse(location)
        location_id and location_id.unlink()
        return True