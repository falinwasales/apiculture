from odoo import api, models, fields
from odoo.exceptions import Warning,UserError
from odoo.tools.translate import _
import logging
from . import prestapi
from .prestapi import PrestaShopWebService,PrestaShopWebServiceDict,PrestaShopWebServiceError,PrestaShopAuthenticationError

_logger = logging.getLogger(__name__)

class ConnectorInstance(models.Model):
    _inherit = 'connector.instance'



    is_barcode = fields.Boolean(string='Check Barcode code')
    is_reference = fields.Boolean(string='Check Default code')
    
    @api.model
    def _get_list(self):
        try:
            return_list=[]
            config_ids=self
            if not config_ids:
                config_ids = self.search([('active','=',True)])
            if config_ids:
                for config_id in config_ids:
                    url=config_id[0].user
                    key=config_id[0].pwd
                    try:
                        prestashop = PrestaShopWebServiceDict(url,key)
                    except PrestaShopWebServiceError as e:
                        raise UserError(_('Error %s')%str(e))
                    if prestashop:
                        languages=prestashop.get('languages',options={'display': '[id,name]','filter[active]': '1'})
                        if 'languages' in languages:
                            languages = languages['languages']
                        if type(languages['language'])==list:
                            for row in languages['language']:
                                return_list.append((row['id'],row['name']+config_id.instance_name))
                        else:
                            return_list.append((languages['language']['id'],
                            languages['language']['name'] + config_id.instance_name))
            return return_list
        except:
            return return_list
    
    
    ps_language_id = fields.Selection(_get_list, 'Prestashop Language', default=_get_list)


    def refresh_list(self):
        view_ref = self.env['ir.model.data'].get_object_reference('bridge_skeleton', 'connector_instance_form')
        view_id = view_ref and view_ref[1] or False,
        return {
                'type': 'ir.actions.act_window',
                'name': 'Ecomm Configuration',
                'res_model': 'connector.instance',
                'res_id': self._ids[0],
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'target': 'current',
                'nodestroy': True,
                }


    @api.model
    def create(self, vals):
        if 'pwd' in vals:
            vals['pwd']=vals['pwd'].strip()
        if 'user' in vals:
            if not vals['user'].endswith('/'):
                vals['user'] += '/'
            if not vals['user'].endswith('api/'):
                raise Warning(("Api url must in the format ( base url of your prestashop + 'api' )"))
        return super(ConnectorInstance, self).create(vals)
	
    
    def write(self, vals):
        if 'pwd' in vals:
            vals['pwd']=vals['pwd'].strip()
        if 'user' in vals:
            if not vals['user'].endswith('/'):
                vals['user'] += '/'
            if not vals['user'].endswith('api/'):
                raise Warning(("Api url must in the format ( base url of your prestashop + 'api' )"))
        return super(ConnectorInstance, self).write(vals)
	
    
    def test_prestashop_connection(self):
        flag=0
        message="<h2>Connected successfully...you can start syncing data now.</h2>"
        extra_message=""
        try:
            url = self.user
            key = self.pwd
            try:
                prestashop = PrestaShopWebServiceDict(url,key)
                languages = prestashop.get("languages",options={'filter[active]':'1',})
                self.connection_status = True
                if 'languages' in languages:
                    languages = languages['languages']
                if 'language' in languages:
                    if type(languages['language'])==list:
                        extra_message = 'Currently you have %s languages active on your Prestashop. Please use, use our POB Extension for MultiLanguage, in order to synchronize language wise.'%str(len(languages['language']))
            except Exception as e:
                self.connection_status = False
                message='Connection Error: '+str(e)+'\r\n'
                try:
                    import requests
                    from lxml import etree
                    client = requests.Session()
                    client.auth=(key, '')
                    response=client.request('get',url)
                    msg_tree=etree.fromstring(response.content)
                    for element in msg_tree.xpath("//message"):
                        message=message+element.text
                except Exception as e:
                    message='\r\n'+message+str(e)
        except:
            message=reduce(lambda x, y: x+y,traceback.format_exception(*sys.exc_info()))
        finally:
            message = message + '<br />' + extra_message
            return self.env['message.wizard'].genrated_message(message)

    
    def _create_prestashop_connection(self):
        status = False
        instance_id = self._context.get('instance_id', False)
        prestashop = False
        ps_lang_id = 0
        if instance_id:
            try:
                instance_obj = self.browse(instance_id)
                prestashop = PrestaShopWebServiceDict(instance_obj.user,instance_obj.pwd)
                languages = prestashop.get("languages",options={'filter[active]':'1'})
                ps_lang_id = instance_obj.ps_language_id or 0
                status = True
            except Exception as e:
                raise Warning(" Problem in Connecting with prestashop " + str(e))
        if status:
            try:
                schema = prestashop.get('erp_product_template_merges', options={'schema':'blank'})
            except Exception as e:
                raise Warning('Kindly Provide Permission to POB Web Services On Prestashop ' + str(e))
        return {
            'status' : status,
            'prestashop' : prestashop,
            'ps_lang_id' : ps_lang_id
        }
        