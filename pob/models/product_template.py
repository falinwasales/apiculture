from odoo import api, models, fields
from odoo.exceptions import Warning
from odoo.addons.bridge_skeleton.models.core.res_partner import _unescape
import logging
_logger = logging.getLogger(__name__)
class ProductTemplate(models.Model):
    _inherit = "product.template"


    wk_barcode = fields.Char(string='Barcode')

    @api.model
    def create(self, vals):
        ctx = dict(self._context or {})
        ecomm_cannels = dict(self.env['connector.snippet']._get_ecomm_extensions()).keys()
        instance_id = ctx.get('instance_id',False)
        ecomm_id = vals.get('ecomm_id','')
        template_id = False
        if any(key in ctx for key in ecomm_cannels) and instance_id:
            instance_obj = self.env['connector.instance'].browse(instance_id)
            vals['wk_barcode'] = _unescape(vals.pop('barcode',False))
            if instance_obj.is_reference and vals.get('default_code',False):
                template_id = self.search([('config_sku','=',vals.get('default_code'))],limit=1)
                _logger.info("---template_id case default_code search --%r",template_id)
            if instance_obj.is_barcode and not template_id and vals.get('wk_barcode'):
                template_id = self.search([('wk_barcode','=',vals.get('wk_barcode'))],limit=1)
                _logger.info("---template_id case barcode search --%r",template_id)
        _logger.info("------template_id ---- prod_template---%r",template_id)
        if template_id:
            channel = "".join(list(set(ctx.keys())&set(ecomm_cannels))) or 'Ecommerce' + str(instance_id)
            self.env['connector.snippet'].create_odoo_connector_mapping('connector.template.mapping', ecomm_id,template_id.id, instance_id, is_variants=True, created_by=channel)
            return template_id
        else:
            template_id = super(ProductTemplate,self).create(vals)
        return template_id