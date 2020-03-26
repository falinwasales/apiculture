from odoo import api, models, fields
import logging
_logger = logging.getLogger(__name__)

class ConnectorSnippet(models.TransientModel):
    _inherit = 'connector.snippet'

    @api.model
    def prestashop_after_order_invoice(self , connection, ecommerce_reference , id_order):
        prestashop = connection.get('prestashop', False)
        return self.update_order_status_prestashop(prestashop, id_order, 2)
       
    @api.model
    def prestashop_after_order_cancel(self , connection, ecommerce_reference , id_order):
        prestashop = connection.get('prestashop', False)
        return self.update_order_status_prestashop(prestashop, id_order, 6)
     
    @api.model
    def prestashop_after_order_shipment(self , connection, ecommerce_reference , id_order):
        prestashop = connection.get('prestashop', False)
        return self.update_order_status_prestashop(prestashop, id_order, 4)

    def update_order_status_prestashop(self, prestashop, id_order, id_order_state):
        status = 'no'
        text = 'Status Successfully Updated'
        try:
            order_his_data = prestashop.get('order_histories', options={'schema': 'blank'})
            order_his_data['order_history'].update({
            'id_order' : id_order,
            'id_order_state' : id_order_state
            })
            state_update = prestashop.add('order_histories?sendemail=1', order_his_data)
            status = 'yes'
        except Exception as e:
            text = 'Status Not Updated For Order Id '+ str(id_order) + ' And Error is ' + str(e)
        return{
            'status':status,
            'text' : text
        }

