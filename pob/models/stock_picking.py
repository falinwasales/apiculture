#!/usr/bin/env python
# -*- coding: utf-8 -*-
##################################################################################
#                                                                                #
#    Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)#
#																				 #
##################################################################################

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def action_sync_tracking_number(self):
        selected_ids = self._context.get('active_ids')
        up_length = 0
        error_message = ''
        message = ''
        presta_id = False
        if selected_ids:
            for k in self.env['stock.picking'].browse(selected_ids):
                sale_order_id = k.sale_id.id
                track_ref = k.carrier_tracking_ref
                if not track_ref:
                    track_ref = ''
                if sale_order_id:
                    check = self.env['connector.order.mapping'].search([('odoo_order_id', '=', sale_order_id)])
                    if check:
                        instance_id = check.instance_id.id
                        if instance_id:
                            connection = self.env['connector.instance'].\
                                with_context({'instance_id':instance_id})._create_prestashop_connection()
                            prestashop = connection.get('prestashop', False)
                            if prestashop:
                                presta_id = check[0].ecommerce_order_id
                                if presta_id:
                                    try:
                                        get_carrier_data = prestashop.get('order_carriers', options={'filter[id_order]':presta_id})
                                    except Exception as e:
                                        error_message="Error %s, Error in getting Carrier Data"%str(e)
                                    try:
                                        if get_carrier_data['order_carriers']:
                                            order_carrier_id = get_carrier_data['order_carriers']['order_carrier']['attrs']['id']
                                            if order_carrier_id:
                                                data = prestashop.get('order_carriers', order_carrier_id)
                                                data['order_carrier'].update({
                                                    'tracking_number' : track_ref,
                                                    })
                                                try:
                                                    return_id = prestashop.edit('order_carriers', order_carrier_id, data)
                                                    up_length = up_length + 1
                                                except Exception as e:
                                                    error_message = error_message + str(e)

                                    except Exception as e:
                                        error_message = error_message + str(e)
        if not error_message:
            if up_length==0:
                message = "No Prestashop Order records fetched in selected stock movement records!!!"
            else:
                message = '%s Carrier Tracking Reference Number Updated to Prestashop!!!'%(up_length)
        else:
            message = "Error in Updating: %s"%(error_message)
        return self.env['message.wizard'].genrated_message(message)
			