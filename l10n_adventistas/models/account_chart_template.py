# coding: utf-8

from odoo import models, api, _

class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    @api.model
    def _get_default_bank_journals_data(self):
        if self == self.env.ref("l10n_adventistas.cuentas_plantilla"):
            return []
        return super(AccountChartTemplate, self)._get_default_bank_journals_data()

    def _create_bank_journals(self, company, acc_template_ref):
        res = super(AccountChartTemplate, self)._create_bank_journals(company, acc_template_ref)
        if self == self.env.ref("l10n_adventistas.cuentas_plantilla"):
            journals = self.env["account.journal"]
            journals_data = [
                {
                    "acc_name": "Bank",
                    "account_type": "bank",
                    "default_account": acc_template_ref[self.env.ref("l10n_adventistas.cta11122110").id],
                    "code": "BNK1",
                },
                {
                    "acc_name": "Cash",
                    "account_type": "cash",
                    "default_account": acc_template_ref[self.env.ref("l10n_adventistas.cta11111110").id],
                    "code": "CSH1",
                },
                {
                    "acc_name": "Transito Pagos Nomina General",
                    "account_type": "bank",
                    "default_account": acc_template_ref[self.env.ref("l10n_adventistas.cta11122150").id],
                    "code": "PANOM",
                },
                {
                    "acc_name": "Activos Fijos",
                    "account_type": "general",
                    "code": "ASSET",
                },
                {
                    "acc_name": "Nomina General",
                    "account_type": "purchase",
                    "code": "NOM_G",
                },
                {
                    "acc_name": "Wallet",
                    "account_type": "purchase",
                    "default_account": acc_template_ref[self.env.ref("l10n_adventistas.cta21411120").id],
                    "code": "WALLE",
                },
                {
                    "acc_name": "Notas Internas",
                    "account_type": "sale",
                    "code": "NF",
                },
            ]
            for acc in journals_data:
                journals += self.env["account.journal"].create({
                    "name": acc["acc_name"],
                    "type": acc["account_type"],
                    "company_id": company.id,
                    "currency_id": acc.get("currency_id", self.env["res.currency"]).id,
                    "default_credit_account_id": acc.get("default_account", False),
                    "default_debit_account_id": acc.get("default_account", False),
                    "sequence": 10,
                    "code": acc["code"],
                })
        return res