# Copyright 2016 Camptocamp SA
# Copyright 2019 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    'name': 'Account Invoice Rounding',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'author': 'Camptocamp, '
              'Agile Business Group, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-invoicing/tree/12.0/'
               'account_invoice_rounding',
    'license': 'AGPL-3',
    'depends': [
        'account'
    ],
    'data': [
        'views/res_config_settings_views.xml'
    ],
    'installable': True,
}
