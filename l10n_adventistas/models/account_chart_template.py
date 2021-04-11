# coding: utf-8

from odoo import models, api, _

class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    @api.model
    def _get_default_bank_journals_data(self):
        if self == self.env.ref("l10n_adventistas.cuentas_plantilla"):
            return {}
        return super(AccountChartTemplate, self)._get_default_bank_journals_data()