#-*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class Partner(models.Model):
    _inherit = 'res.partner'

    no_constant_registro_exonerado = fields.Char("No. CONSTAN. REGISTRO EXONERADO")
    family_res_finance_ids = fields.One2many("honduras_invoices.financial.res.percent", 'partner_id', string="Family resposability")

    def write(self, values):

        self._cr.autocommit(False)

        partner = super().write(values)

        categories = [{category.category_id.id:category.percent} for category in self.family_res_finance_ids]
        categories_ids = {category.category_id for category in self.family_res_finance_ids}

        for category_id in categories_ids:
            percent_sum = sum([category.percent for category in self.family_res_finance_ids if category.category_id == category_id])
            if percent_sum != 100:
                self._cr.rollback()
                raise UserError(_("Category: {} doesn't sum 100!".format(category_id.complete_name)))

        self._cr.commit()

        return partner
