# -*- coding: utf-8 -*-pack
{
    # App information
    'name': 'eCommerce Sendcloud Integration',
    'category': 'Website',
    'version': '13.0',
    'summary': """We are providing following modules, Shipping Operations, shipping, odoo shipping integration,odoo shipping connector, dhl express, fedex, ups, gls, usps, stamps.com, shipstation, bigcommerce, easyship, amazon shipping, sendclound, ebay, shopify.""",
    'description': """""",
    'depends': [
        'website_sale',
        'sendcloud_odoo_integration'
    ],

    'data': [
        'data/ir_config_parameter_data.xml',
        'templates/assests.xml',
        'templates/template.xml',
    ],

    
    'images': ['static/description/sendcloud.png'],
    'author': 'Vraja Technologies',
    'maintainer': 'Vraja Technologies',
    'website':'www.vrajatechnologies.com',
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': '101',
    'currency': 'EUR',
    'license': 'OPL-1',

}
