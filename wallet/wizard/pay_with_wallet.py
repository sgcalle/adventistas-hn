from odoo import fields, models, api
from collections import defaultdict
# from ..util import DefaultOrderedDict
import logging

_logger = logging.getLogger(__name__)


class PayWithWallet(models.TransientModel):
    _name = 'pay.with.wallet'
    _description = 'Pay with wallet...'

    @api.depends("wallet_payment_line_ids")
    def _compute_used_wallet_ids(self):
        for record in self:
            # record.wallet_payment_line_ids = record.wallet_payment_line_ids.filtered(
            #     lambda payment_line_id: payment_line_id.wallet_id)
            record.used_wallet_ids = record.wallet_payment_line_ids.mapped("wallet_id")


    # @api.onchange("wallet_payment_line_ids")
    # def _onchange_wallet_payment_line_ids(self):
    #     for record in self:



    @api.depends("partner_id")
    def _compute_wallet_ids(self):
        self.ensure_one()
        context = self._context
        active_move_ids = context.get("active_id", False)

        if active_move_ids:
            walletCategoryEnv = self.env["wallet.category"]
            available_wallets = walletCategoryEnv
            move_ids = self.env["account.move"].browse(active_move_ids)
            for move_id in move_ids:
                partner_id = move_id.partner_id
                wallet_ids = walletCategoryEnv.search([])

                for wallet_id in wallet_ids:
                    amount_total = walletCategoryEnv.get_wallet_amount(partner_id, wallet_id)

                    if amount_total > -abs(wallet_id.credit_limit):
                        available_wallets += wallet_id

            # family_ids = self.partner_id.family_ids.ids
            self.wallet_ids = available_wallets

    def pay_with_wallet(self):
        self.ensure_one()

        context = self._context
        active_move_ids = context.get("active_ids", False)

        if active_move_ids:

            wallet_payment_line_dict = {wallet_payment_line_id.wallet_id: wallet_payment_line_id.amount
                                        for wallet_payment_line_id in self.wallet_payment_line_ids}

            move_ids = self.env["account.move"].browse(active_move_ids)
            for move_id in move_ids:
                move_id.pay_with_wallet(wallet_payment_line_dict)

    def _get_default_lines(self):
        active_move_ids = self._context.get('active_ids', [])
        if active_move_ids:
            move_ids = self.env["account.move"].browse(active_move_ids)
            move_ids.partner_id.ensure_one()

            wallet_to_apply = move_ids.get_wallet_due_amounts()
            wallet_partner_amounts = {wallet_id: wallet_id.get_wallet_amount(move_ids.partner_id) for wallet_id in
                                      self.env["wallet.category"].search([])}
            wallet_payment_line_ids = self.env["wallet.payment.line"]

            wallet_suggestion_amounts = move_ids.calculate_wallet_distribution(wallet_to_apply, wallet_partner_amounts)

            for wallet_id, amount in wallet_suggestion_amounts.items():
                wallet_payment_line_id = self.wallet_payment_line_ids.create({
                    "wallet_id": wallet_id.id,
                    "amount": amount
                })
                wallet_payment_line_ids += wallet_payment_line_id
            return wallet_payment_line_ids

    partner_id = fields.Many2one("res.partner", required=True)
    wallet_ids = fields.Many2many("wallet.category", compute="_compute_wallet_ids")
    used_wallet_ids = fields.Many2many("wallet.category", compute="_compute_used_wallet_ids")
    wallet_payment_line_ids = fields.One2many("wallet.payment.line", "pay_with_wallet_id", string="Wallets", default=_get_default_lines)


class WalletPaymentLine(models.TransientModel):
    _name = "wallet.payment.line"

    @api.depends("wallet_id", "amount")
    def _compute_partner_amount(self):
        for record in self:
            if record.wallet_id:
                record.partner_amount = record.wallet_id.get_wallet_amount(record.pay_with_wallet_id.partner_id) - record.amount

    pay_with_wallet_id = fields.Many2one("pay.with.wallet")
    wallet_id = fields.Many2one("wallet.category", required=True)
    amount = fields.Float()
    partner_amount = fields.Float("Partner amount", readonly=True, compute="_compute_partner_amount")