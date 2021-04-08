# -*- coding: utf-8 -*-

from odoo import models, _, api, exceptions, fields


class PosConfig(models.Model):
    """ Adds constraints """
    _inherit = "pos.config"

    is_pos_pr_discount = fields.Boolean(default=False)
    school_code_ids = fields.Many2many('school_base.school_code')
    available_school_code_ids = fields.Many2many('school_base.school_code')

    @api.depends('company_id')
    def _compute_available_school_code_ids(self):
        for session in self:
            session.available_school_code_ids = session.mapped('company_id.district_code_ids.school_code_ids')

    @api.constrains('payment_method_ids')
    def check_if_there_is_discount_payment_method(self):
        for pos_config_id in self:
            discount_payment_method = pos_config_id.payment_method_ids.filtered(lambda payment_method: payment_method.is_pos_pr_discount)
            if discount_payment_method:
                raise exceptions.ValidationError(_("%s is only for aesthetic use") % discount_payment_method.name)
