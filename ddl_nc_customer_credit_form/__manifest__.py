# -*- coding: utf-8 -*-
{
    'name': 'DDL Customer Credit Form',
    'version': '1.0',
    'summary': """Customer Credit Form""",
    'description': """Customer Credit Form""",
    'category': 'Generic Modules',
    'author': 'Doodle Inc, Mursalin',
    'company': 'Doodle Inc',
    'website': "https://doodleinc.com",
    'depends': ['contacts','sale','account','stock','report_last_page','crm','purchase'],
    'data': [
             'security/ir.model.access.csv',
             'data/allowed_brand_group.xml',
             'data/stock_return_location_data.xml',
             'views/contact_view.xml',
             'views/partner_related_views.xml',
             'views/product_brand_view.xml',
             'views/sold_item_view.xml',
             'views/lead_details_view.xml',
             'views/salesperson_target_view.xml',
             'views/stock_return_widget_view.xml',
             'views/stock_product_return_view.xml',
             'views/return_report_wizard_view.xml',
             'views/lead_view.xml',
             'views/salesperson_allowed_product_brand_view.xml',
             'views/show_salesperson.xml',
             'views/stock_picking_inherit_view.xml',
             'report/custom_invoice.xml',
             'report/application_for_credit.xml',
             'report/report.xml',
             'data/page_format.xml',
             'data/allowed_brand_rule.xml',
             'data/show_lead_rule.xml',
             'data/allowed_pharmacy_rule.xml',
             ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
