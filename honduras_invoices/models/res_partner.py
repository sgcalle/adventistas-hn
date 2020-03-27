#-*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import AccessError, UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    no_constant_registro_exonerado = fields.Char("No. CONSTAN. REGISTRO EXONERADO")
    family_res_finance_ids = fields.One2many("honduras_invoices.financial.res.percent", 'partner_id', string="Family resposability")

    def _check_category_sum(self):
        for record in self:
            categories = [{category.category_id.id:category.percent} for category in record.family_res_finance_ids]
            categories_ids = {category.category_id for category in record.family_res_finance_ids}

            for category_id in categories_ids:
                percent_sum = sum([category.percent for category in record.family_res_finance_ids if category.category_id == category_id])
                if percent_sum != 100:
                    raise UserError(_("Category: {} doesn't sum 100!".format(category_id.complete_name)))


    @api.model
    def create(self, vals):
        try:
            partners = super().create(vals)
            partners._check_category_sum()
            return partners
        except:
            self._cr.rollback()
            raise


    def write(self, vals):
        try:
            partners = super().write(vals)
            self._check_category_sum()
            return partners
        except:
            self._cr.rollback()
            raise
