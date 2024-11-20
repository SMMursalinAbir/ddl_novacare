# -*- coding: utf-8 -*-
{
    'name': 'DDL Get Location',
    'version': '1.0',
    'summary': """DDL Get Location""",
    'description': """DDL Get Location""",
    'category': 'Generic Modules',
    'author': 'Doodle Inc, Mursalin',
    'company': 'Doodle Inc',
    'website': "https://doodleinc.com",
    'depends': ['crm','ddl_nc_customer_credit_form'],
    'data': ['security/ir.model.access.csv',
             'views/get_location_view.xml',
             'views/get_salesperson_map_view.xml',



             ],
    'assets': {
            'web.assets_frontend': [
                'ddl_get_location/static/src/js/get_location.js',
            ],
        },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
