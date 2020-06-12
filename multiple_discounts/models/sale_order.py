# -*- coding: utf-8 -*-

from odoo import models, fields, _, api


def get_parent_category(category_id):
    single_list = [category_id]

    if category_id.parent_id:
        single_list.extend(get_parent_category(category_id.parent_id))
        return single_list
    else:
        return single_list

class SaleOrder(models.Model):

    _inherit = "sale.order"

    def apply_discount(self):

        for order_id in self:
            write_lines = []
            discount_ids = order_id.partner_id.discount_ids

            for order_line_id in order_id.order_line:
                invoice_line_categories = get_parent_category(order_line_id.product_id.categ_id)
                discount_applicable = discount_ids.filtered(
                    lambda discount: discount.category_id in invoice_line_categories)

                for discount in discount_applicable:
                    percent = discount.percent
                    discount_count = -order_line_id.price_subtotal * (percent/100)

                    order_line_create = {
                        "product_id": discount.product_id.get_single_product_variant().get("product_id", False),
                        "price_unit": discount_count,
                        # "analytic_account_id": discount.analytic_account_id.id,
                    }

                    if order_line_id.tax_id:
                        order_line_create.update({"tax_id": [(6, 0, order_line_id.tax_id.ids)]})


                    write_lines.append((0, 0, order_line_create))

            order_id.write({
                "order_line": write_lines
            })


    @api.model
    def create(self, vals):
        order_ids = super().create(vals)

        # We add the discounts here if context's apply_discounts variable is set True
        for order_id in order_ids:

            # 2020/06/12: We don't do it due we want to be applied every time
            #  if self._context.get("apply_discounts", False):
            order_id.apply_discount()

        return order_ids
