# Copyright 2016 Camptocamp SA
# Copyright 2019 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api
from odoo.tools.float_utils import float_round, float_compare
from odoo.tools.translate import _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _swedish_add_invoice_line(self, rounded_total, delta, precision):
        """ Create a invoice_line with the diff of rounding """
        self.ensure_one()
        company = self.company_id
        if not self.global_round_line_id.id:
            global_round_line = self.env['account.invoice.line'].create({
                'name': _('Rounding'),
                'price_unit': -delta,
                'account_id': company.tax_calculation_rounding_account_id.id,
                'invoice_id': self.id,
                'is_rounding_line': True,})
            self.write({'global_round_line_id': global_round_line.id})
        elif float_compare(self.global_round_line_id.price_unit, -delta,
                           precision_digits=precision) != 0:
            self.global_round_line_id.write({'price_unit': -delta})

        amount_untaxed = float_round(self.amount_untaxed - delta,
                                     precision_digits=precision)
        return {'amount_total': rounded_total,
                'amount_untaxed': amount_untaxed}

    @api.multi
    def _all_invoice_tax_line_computed(self):
        """ Check if all taxes have been computed on invoice lines
        :return boolean True if all tax were computed
        """
        self.ensure_one()
        taxes = self.mapped(
            'invoice_line_ids.invoice_line_tax_ids').filtered(
            lambda t: not t.price_include)
        computed_taxes = self.mapped('tax_line_ids')
        return len(taxes) == len(computed_taxes)

    @api.multi
    def _swedish_round_globally(self, rounded_total, delta, precision):
        """ Add the diff to the biggest tax line
        This ajustment must be done only after all tax are computed
        """
        self.ensure_one()
        res = {}
        # we check that all tax lines have been computed
        if not self._all_invoice_tax_line_computed():
            return res
        ajust_line = None
        for tax_line in self.tax_line_ids:
            if not ajust_line or tax_line.amount > ajust_line.amount:
                ajust_line = tax_line
        if ajust_line:
            amount = ajust_line.amount - delta
            amount_tax = float_round(
                self.amount_tax - delta, precision_digits=precision)
            res = {
                'amount_total': rounded_total,
                'amount_tax': amount_tax,
                'ajust_line': ajust_line,
                'ajust_line_amount': amount,}
        return res

    @api.multi
    def _compute_swedish_rounding(self):
        """
        Depending on the method defined, we add an invoice line or adapt the
        tax lines to have a rounded total amount on the invoice
        :return dict: updated values for _amount_all
        """
        self.ensure_one()
        prec = self.env['decimal.precision'].precision_get('Account')
        # avoid recusivity
        if 'swedish_write' in self.env.context:
            return {}
        company = self.company_id
        round_method = company.tax_calculation_rounding_method

        if not round_method:
            return {}
        if round_method[:7] != 'swedish':
            return {}
        rounding_prec = company.tax_calculation_rounding
        if rounding_prec <= 0.00:
            return {}
        rounded_total = float_round(self.amount_total,
                                    precision_rounding=rounding_prec)

        if float_compare(rounded_total, self.amount_total,
                         precision_digits=prec) == 0:
            return {}

        # To avoid recursivity as we need to write on invoice or
        # on objects triggering computation of _amount_all
        ctx = self.env.context.copy()
        ctx['swedish_write'] = True

        delta = float_round(self.amount_total - rounded_total,
                            precision_digits=prec)
        if round_method == 'swedish_add_invoice_line':
            return self._swedish_add_invoice_line(rounded_total, delta, prec)
        elif round_method == 'swedish_round_globally':
            return self._swedish_round_globally(rounded_total, delta, prec)
        return {}

    @api.multi
    @api.depends(
        'invoice_line_ids.price_subtotal', 'tax_line_ids.amount',
        'tax_line_ids.amount_rounding', 'currency_id', 'company_id',
        'date_invoice', 'type')
    def _compute_amount(self):
        """ Add swedish rounding computing
        Makes sure invoice line for rounding is not computed in totals
        """
        super(AccountInvoice, self)._compute_amount()
        for invoice in self:
            if invoice.type in ('out_invoice', 'out_refund'):
                if invoice.global_round_line_id.id:
                    line = invoice.global_round_line_id
                    if line:
                        invoice.amount_untaxed -= line.price_subtotal
                swedish_rounding = self._compute_swedish_rounding()
                if swedish_rounding:
                    invoice.amount_total = swedish_rounding['amount_total']
                    if 'amount_tax' in swedish_rounding:
                        invoice.amount_tax = swedish_rounding['amount_tax']
                    elif 'amount_untaxed' in swedish_rounding:
                        invoice.amount_untaxed = (
                            swedish_rounding['amount_untaxed'])
                    if 'ajust_line' in swedish_rounding:
                        swedish_rounding['ajust_line'].amount = (
                            swedish_rounding['ajust_line_amount'])

    global_round_line_id = fields.Many2one(
        'account.invoice.line',
        string='Invoice Line for total rounding',)
