# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MultipleDiscounts(models.Model):
    _name = 'multiple_discounts.discount'
    _description = 'Multiple Discounts applicable to customers'

    name = fields.Char("Name", required=True)
    percent = fields.Float("Percent", required=True)
    category_id = fields.Many2one("product.category", required=True)
    
    account_id = fields.Many2one('account.account', required=True, string='Account', index=True, ondelete="cascade", domain=[('deprecated', '=', False)])
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True)
