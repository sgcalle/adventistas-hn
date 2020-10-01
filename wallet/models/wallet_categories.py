from odoo import fields, models, api
from odoo.tools import float_round


class WalletCategory(models.Model):
    _name = 'wallet.category'
    _description = 'Wallet categories'

    name = fields.Char(required=True)

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    default_wallet_category_id = fields.Many2one('wallet.category', related='company_id.default_wallet_category_id', store=True)
    is_default_wallet = fields.Boolean(compute='_compute_is_default_wallet', store=True)

    journal_category_id = fields.Many2one("account.journal", domain="[('type', '=', 'sale')]")
    account_id = fields.Many2one("account.account", "Account", default=lambda self: int(self.env["ir.config_parameter"].get_param('wallet.default_account_id')))
    category_id = fields.Many2one("product.category", "Category", required=True)
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    credit_limit = fields.Float("Credit limit", default=lambda self: float(
        self.env["ir.config_parameter"].get_param('wallet.wallet_credit_limit')))
    product_external_relation_id = fields.Char(related="product_id.categ_id.external_relation_id")

    @api.depends('default_wallet_category_id')
    def _compute_is_default_wallet(self):
        for wallet in self:
            wallet.is_default_wallet = wallet.id == wallet.default_wallet_category_id.id

    @api.model
    def default_get(self, vals):
        # company_id is added so that we are sure to fetch a default value from it to use in repartition lines, below
        rslt = super().default_get(vals + ['company_id'])
        return rslt

    def get_wallet_amount(self, partner_id, wallet_category_id=False):

        if type(partner_id) == int:
            partner_id = self.env["res.partner"].browse(partner_id)

        if type(wallet_category_id) == int:
            wallet_category_id = self.env["wallet.category"].browse([wallet_category_id])
        elif not wallet_category_id:
            wallet_category_id = self

        if wallet_category_id:
            wallet_moves = self.env["account.move"].search(
                [("partner_id", "=", partner_id.id), ('state', '=', 'posted')]).invoice_line_ids.filtered(
                lambda line_id: line_id.product_id in wallet_category_id.product_id)

            if wallet_moves:
                amount_total = sum(wallet_moves.mapped(lambda move_line: move_line.price_unit if move_line.move_id.type == 'out_invoice' else -move_line.price_unit))
                return float_round(amount_total, precision_digits=self.company_id.currency_id.decimal_places)

        return 0

    @api.model
    def create(self, values):
        wallet_id = super().create(values)

        if "product_id" not in values:
            product_id = self.env["product.product"].create({
                "categ_id": wallet_id.category_id.id,
                "property_account_income_id": wallet_id.account_id.id,
                "taxes_id": False,
                "type": "service",
                "list_price": 0.0,
                "supplier_taxes_id": False,
                "name": wallet_id.name,
            })

            wallet_id.product_id = product_id

        return wallet_id

    def get_wallet_by_category_id(self, category_id):
        if not category_id:
            return self.env.company.default_wallet_category_id

        wallet_id = self.env["wallet.category"].search([("category_id", "=", category_id.id)])
        if not wallet_id:
            wallet_id = self.get_wallet_by_category_id(category_id.parent_id)

        wallet_id = wallet_id[0]
        return wallet_id

    def find_next_available_wallet(self, partner_id, category_id):

        wallet_id = self.env["wallet.category"].search([("category_id", "=", category_id.id)])
        if not wallet_id:
            if category_id.parent_id:
                wallet_id = self.find_next_available_wallet(partner_id, category_id.parent_id)
            else:
                wallet_id = self.env.company.default_wallet_category_id

        if self.get_wallet_amount(partner_id, wallet_id) > -abs(wallet_id.credit_limit):
            return wallet_id
        elif category_id == self.env.company.default_wallet_category_id:
            return False
        else:
            if category_id.parent_id:
                wallet_id = self.find_next_available_wallet(partner_id, category_id.parent_id)
            else:
                wallet_id = self.env.company.default_wallet_category_id
            return wallet_id

