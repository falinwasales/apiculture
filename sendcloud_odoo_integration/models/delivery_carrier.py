import time
from requests import request
import requests
from odoo import models, fields, api, _
import logging
import simplejson as json
from requests.auth import HTTPBasicAuth
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError
import binascii
import base64
import requests

_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("sendcloud", "Sendcloud")])
    sendcloud_service_id = fields.Many2one('sendcloud.shipping.services',string="Sendcloud Service")
    location_required = fields.Boolean('Location Required')

    delivery_type_sendcloud = fields.Selection(
        [('fixed', 'Sendcloud Fixed Price'), ('base_on_rule', 'Sendcloud Based on Rules')],
        string='Sendcloud Pricing',
        default='fixed')

    def sendcloud_rate_shipment(self, order):
        if self.delivery_type_sendcloud == 'fixed':
            return self.fixed_rate_shipment(order)
        if self.delivery_type_sendcloud == 'base_on_rule':
            self._get_available_service(order)
            return self.base_on_rule_rate_shipment(order)

    def sendcloud_order_request_data(self,picking):
        receipient_address = picking.partner_id
        picking_company_id = picking.picking_type_id.warehouse_id.partner_id

        if picking.sale_id.sendcloud_service_id:
            sendcloud_service_id = picking.sale_id.sendcloud_service_id.sendcloud_service_id or ""
        else:
            sendcloud_service_id = self.sendcloud_service_id and self.sendcloud_service_id.sendcloud_service_id or ""

        parcel={
            "name":  "%s" % (receipient_address.name),
            "company_name": "%s" % (receipient_address.name),
            "address":"%s" % (picking.sale_id.sendcloud_shipping_location_id.street if picking.sale_id.sendcloud_shipping_location_id.street else receipient_address.street or ""),
            "house_number": "%s"%(receipient_address.street2),
            "city": "%s"% (picking.sale_id.sendcloud_shipping_location_id.city if picking.sale_id.sendcloud_shipping_location_id.city else receipient_address.city or ""),
            "postal_code": "%s" % (picking.sale_id.sendcloud_shipping_location_id.zip if picking.sale_id.sendcloud_shipping_location_id.zip else receipient_address.zip or ""),
            "telephone": "%s" % (receipient_address.phone or ""),
            "request_label": True,
            "email": "%s" % (receipient_address.email or ""),
            "data": [],
            "country": "%s" % (receipient_address.country_id and receipient_address.country_id.code or ""),
            "shipment": {
              "id": sendcloud_service_id
            },
            "weight": "%s"%(picking.shipping_weight),
            "order_number": "%s"%(picking.id),
            "insured_value": 0.0
            # "to_service_point" : picking.sale_id.sendcloud_shipping_location_id.send_cloud_location_id or ""
          }
        if self.location_required:
            parcel.update({"to_service_point" : picking.sale_id.sendcloud_shipping_location_id.send_cloud_location_id})
            sendcloud_request_data={"parcel": parcel}
        else:
       	    sendcloud_request_data={"parcel": parcel}
        return sendcloud_request_data


    def sendcloud_api_calling_function(self, api_url, request_data):
        data = "%s:%s" % (self.company_id and self.company_id.sendcloud_api_key, self.company_id and self.company_id.sendcloud_api_secret)
        encode_data = base64.b64encode(data.encode("utf-8"))
        authrization_data = "Basic %s" % (encode_data.decode("utf-8"))
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization':authrization_data}
        data = json.dumps(request_data)
        try:
            _logger.info("Easyship URL : %s \n Sendcloud Request Data : %s" % (api_url, data))
            response_body = request(method='POST', url=api_url, data=data, headers=headers)
        except Exception as e:
            raise ValidationError(e)
        return response_body

    @api.model
    def sendcloud_send_shipping(self, pickings):
        for picking in pickings:
            try:
                request_data = self.sendcloud_order_request_data(picking)
                api_url = "%s/parcels"%(self.company_id and self.company_id.sendcloud_api_url)
                response_data = self.sendcloud_api_calling_function(api_url, request_data)
            except Exception as e:
                raise ValidationError(_("\n Response Data : %s") % (e))
            if response_data.status_code in [200, 201]:
                response_data = response_data.json()
                _logger.info("Easyship Response Data : %s" % (response_data))
                if response_data.get("parcel") and response_data.get("parcel").get("id"):
                    picking.sendcloud_parcel_id = response_data.get("parcel").get("id")
                    picking.sendcloud_label_url =response_data.get("parcel").get("label")
                    picking.sendcloud_tracking_page_url =response_data.get("parcel").get("tracking_url")
                    picking.sendcloud_shipment_uuid =response_data.get("parcel").get("shipment_uuid")
                    picking.sendcloud_external_order_id=response_data.get("parcel").get("external_order_id")
                    picking.sendcloud_external_shipment_id= response_data.get("parcel").get("external_shipment_id")
                    shipping_data = {
                        'exact_price': 0.0,
                        'tracking_number': response_data.get("parcel").get("tracking_number")}
                    shipping_data = [shipping_data]
                    return shipping_data
                else:
                    raise ValidationError(_("Response Data : %s ") % (response_data))
            else:
                raise ValidationError(
                    _("Response Code : %s Response Data : %s ") % (response_data.status_code, response_data.text))

    def _get_available_service(self, order):
        self.ensure_one()
        total = weight = volume = quantity = 0
        total_delivery = 0.0
        for line in order.order_line:
            if line.state == 'cancel':
                continue
            if line.is_delivery:
                total_delivery += line.price_total
            if not line.product_id or line.is_delivery:
                continue
            qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
            weight += (line.product_id.weight or 0.0) * qty
            volume += (line.product_id.volume or 0.0) * qty
            quantity += qty
        total = (order.amount_total or 0.0) - total_delivery

        total = order.currency_id._convert(
            total, order.company_id.currency_id, order.company_id, order.date_order or fields.Date.today())

        return self._get_available_service_from_picking(total, weight, volume, quantity,order)

    def _get_available_service_from_picking(self, total, weight, volume, quantity,order):
        price = 0.0
        criteria_found = False
        price_dict = {'price': total, 'volume': volume, 'weight': weight, 'wv': volume * weight, 'quantity': quantity}
        for line in self.price_rule_ids:
            test = safe_eval(line.variable + line.operator + str(line.max_value), price_dict)
            if test:
                price = line.list_base_price + line.list_price * price_dict[line.variable_factor]
                criteria_found = True
                order.sendcloud_service_id = line.sendcloud_service_id and line.sendcloud_service_id.id
                break
        if not criteria_found:
            raise UserError(_("No price rule matching this order; delivery cost cannot be computed."))

        return price



class CustomPriceRule(models.Model):
    _inherit = "delivery.price.rule"

    sendcloud_service_id = fields.Many2one('sendcloud.shipping.services', string="Sendcloud Service")
