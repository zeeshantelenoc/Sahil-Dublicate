# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api,_
import pdb
import json
from odoo.exceptions import AccessError, UserError, ValidationError

class ContactTypeCus(models.Model):
    _inherit = 'res.partner'

    is_customer = fields.Boolean("Is Customer")
    is_vendor = fields.Boolean("Is Vendor")
    is_employee = fields.Boolean("Is Employee")
    is_workers = fields.Boolean("Is Worker")
    cash_customers = fields.Boolean("Cash Customer")
    cash_limits = fields.Integer("Cash Limit")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    Worker_id = fields.Many2one('res.partner', 'Worker')

    @api.constrains('order_line')
    def cash_limit(self):
        limit = self.env['res.partner'].search([('name', '=', self.partner_id.name)])
        for rec in limit:
            total_amount = json.loads(self.tax_totals_json)['amount_total']
            if total_amount > rec.cash_limits:
                raise ValidationError(_('This customer cash limit is '+str(rec.cash_limits)+' please select the another customer.'))



class PurchaseOrderCus(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES,
                                 change_default=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('is_vendor','=',True)]",
                                 help="You can find a vendor by its Name, TIN, Email or Internal Reference.")


class AccountCus(models.Model):
    _inherit = 'account.move'

    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict')

    @api.onchange('move_type')
    def onchange_material_type(self):
        for rec in self:
            inv_type = rec._context.get('default_move_type')

            if inv_type in ['out_invoice']:
                return {'domain': {'partner_id': [('is_customer', '=', True)]}}
            if inv_type in ['in_invoice']:
                return {'domain': {'partner_id': [('is_vendor', '=', True)]}}
