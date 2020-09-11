# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import MissingError

class ResPartnerReportCollectionStub(models.AbstractModel):
    _name = "report.honduras_tuition_plan.res_partner_report_collection_stub"

    @api.model
    def _get_report_values(self, docids, data=None):
        partner_obj = self.env["res.partner"]

        partner_ids = self.env.context.get("active_ids", [])
        partners = partner_obj.browse(partner_ids or docids)

        no_tuition_plan = partner_obj
        for partner in partners.filtered(lambda p: p.person_type == "student"):
            tuition_plan = partner.tuition_plan_ids.filtered(lambda t: partner.grade_level_id.id in t.grade_level_ids.ids)
            if not tuition_plan:
                tuition_plan = partner.default_tuition_plan_ids.filtered(lambda t: partner.grade_level_id.id in t.grade_level_ids.ids)
            if tuition_plan:
                tuition_plan = tuition_plan[0]
            else:
                no_tuition_plan |= partner
        
        if no_tuition_plan:
            raise MissingError("The following students have no valid tuition plan: %s" % ", ".join(no_tuition_plan.mapped("name")))

        details = {}
        for partner in partners.filtered(lambda p: p.person_type == "student"):
            tuition_plan = partner.tuition_plan_ids.filtered(lambda t: partner.grade_level_id.id in t.grade_level_ids.ids)
            if not tuition_plan:
                tuition_plan = partner.default_tuition_plan_ids.filtered(lambda t: partner.grade_level_id.id in t.grade_level_ids.ids)
            details[partner.id] = {
                "tuition_plan": tuition_plan[0],
                "start_year": tuition_plan.installment_ids[0].date.year,
                "installments": [],
            }
            for installment in tuition_plan.installment_ids:
                details[partner.id]["end_year"] = installment.date.year
                if installment.product_ids:
                    self._cr.execute("SAVEPOINT collection_stub")
                    sales = installment.with_context(
                        students=partner,
                        override_sale_order_name="For Collection Stub",
                        automation="quotation").execute()
                    details[partner.id]["installments"].append((installment.date.month, sum(sales.mapped("amount_total"))))
                    try:
                        self._cr.execute("ROLLBACK TO SAVEPOINT collection_stub")
                        self.pool.clear_caches()
                        self.pool.reset_changes()
                    except psycopg2.InternalError:
                        pass

        return {
            "doc_ids": partner_ids,
            "doc_model": "res.partner",
            "docs": partners,
            "details": details,
        }