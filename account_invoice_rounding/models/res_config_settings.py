# Copyright 2016 Camptocamp SA
# Copyright 2019 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_calculation_rounding = fields.Float(
        related='company_id.tax_calculation_rounding',
        readonly=False)
    tax_calculation_rounding_method = fields.Selection(
        related='company_id.tax_calculation_rounding_method',
        readonly=False)
    tax_calculation_rounding_account_id = fields.Many2one(
        related='company_id.tax_calculation_rounding_account_id',
        readonly=False)
