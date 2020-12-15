from odoo import api, models, fields

class ConnectorSnippet(models.TransientModel):
    _inherit = 'connector.snippet'


    @api.model
    def _get_ecomm_extensions(self):
        ecommece_channels = super(ConnectorSnippet,self)._get_ecomm_extensions()
        ecommece_channels.append(('prestashop','Prestashop'))
        return ecommece_channels

    @api.model
    def get_quantity(self,obj_pro, instance_id):
        """
            to get quantity of product or product template
            @params : product template obj or product obj,instance_id
            @return : quantity in hand or quantity forecasted
        """
        quantity = 0.0
        config_id = self.env['connector.instance'].browse(instance_id)
        ctx = self._context.copy() or {}
        if not 'warehouse' in ctx:
            ctx.update({
                'warehouse': config_id.warehouse_id.id
            })
        qty = obj_pro.with_context(ctx)._product_available()
        if config_id.connector_stock_action =="qoh":
            quantity = qty[obj_pro.id]['qty_available'] - qty[obj_pro.id]['outgoing_qty']
        else:
            quantity = qty[obj_pro.id]['virtual_available']
        if type(quantity) == str:
            quantity = quantity.split('.')[0]
        if type(quantity) == float:
            quantity = quantity.as_integer_ratio()[0]
        return quantity
    
    @api.model
    def create_prestashop_connector_odoo_mapping(self, mapping_data, model):
        if model=='connector.product.mapping':
            template_id = self.env['product.product'].browse(mapping_data.get('odoo_id')).product_tmpl_id.id
            ecomm_combination_id =  self._context.get('ecomm_combination_id',0)
            if template_id and not mapping_data.get('ecomm_combination_id'):
                mapping_data.update({
                    'odoo_tmpl_id':template_id,
                    'ecomm_combination_id':ecomm_combination_id
                    })
        return mapping_data
        


    
    @api.model
    def _get_link_rewrite(self, zip, string):
        if type(string)!=str:
            string =string.encode('ascii','ignore')
            string=str(string)
        import re
        string=re.sub('[^A-Za-z0-9]+',' ',string)
        string=string.replace(' ','-').replace('/','-')
        string=string.lower()
        return string