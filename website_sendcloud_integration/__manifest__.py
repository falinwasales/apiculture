# -*- coding: utf-8 -*-pack
{
    # App information
    'name': 'Website Sendcloud Integration',
    'category': 'Website',
    'version': '13.0.1',
    'summary': """.""",
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

    'author': 'Vraja Technologies',
    'maintainer': 'Vraja Technologies',

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': '199',
    'currency': 'EUR',
    'license': 'LGPL-3',
}
