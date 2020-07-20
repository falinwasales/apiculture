# -*- coding: utf-8 -*-pack
{
    # App information
    'name': 'Sendcloud Integration',
    'category': 'Website',
    'version': '12.0.03.10.2019',
    'summary': """Sendcloud Shipping Integration will help you connect with Multiple Shipping Carrier with Odoo.""",
    'description': """""",
    'depends': ['delivery','sale'],
    'data': ['views/res_company.xml',
             'views/delivery_carrier_view.xml',
             'security/ir.model.access.csv',
             'views/sendcloud_shipping_services.xml',
             'views/stock_picking.xml',
             'views/sale_view.xml',
             ],
    
    'images': ['static/description/sendcloud.png'],
    'author': 'Vraja Technologies',
    'maintainer': 'Vraja Technologies',
    'website':'www.vrajatechnologies.com',
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': '125',
    'currency': 'EUR',
    'license': 'OPL-1',

}
