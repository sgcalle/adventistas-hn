# -*- coding: utf-8 -*-

from odoo import models, _, api, exceptions, fields


class PosConfig(models.Model):
    """ Adds constraints """
    _inherit = "pos.config"

    is_pos_pr_discount = fields.Boolean(default=False)

    @api.constrains('payment_method_ids')
    def check_if_there_is_discount_payment_method(self):
        for pos_config_id in self:
            discount_payment_method_id = self.env.ref('pos_pr.discount_payment_method')
            if discount_payment_method_id in pos_config_id.payment_method_ids:
                raise exceptions.ValidationError(_("%s is only for aesthetic use") % discount_payment_method_id.name)
