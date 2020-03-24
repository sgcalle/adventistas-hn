#-*- coding: utf-8 -*-

from odoo import fields, models

class Partner(models.Model):
    _inherit = 'res.partner'

    no_constant_registro_exonerado = fields.Char("No. CONSTAN. REGISTRO EXONERADO")
    family_res_finance_ids = fields.One2many("adm_uni.financial.res.percent", 'partner_id', string="Family resposability")
