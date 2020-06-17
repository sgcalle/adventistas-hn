#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for payslip in self.filtered(lambda p: p.move_id and p.move_id.state == 'draft'):
            data = {}

            # ALLOWANCES AND DEDUCTIONS
            adjustments = {}
            matched = payslip.contract_id.allowance_ids.filtered(
                lambda a: all([a.debit_account_id, a.credit_account_id]))
            if matched:
                adjustments["Contract Allowances"] = matched
            matched = payslip.contract_id.other_allowance_ids.filtered(
                lambda a: all([a.debit_account_id, a.credit_account_id, a.date >= payslip.date_from, a.date <= payslip.date_to]))
            if matched:
                adjustments["Other Contract Allowances"] = matched
            matched = payslip.contract_id.deduction_ids.filtered(
                lambda a: all([a.debit_account_id, a.credit_account_id]))
            if matched:
                adjustments["Contract Deductions"] = matched
            matched = payslip.contract_id.other_deduction_ids.filtered(
                lambda a: all([a.debit_account_id, a.credit_account_id, a.date >= payslip.date_from, a.date <= payslip.date_to]))
            if matched:
                adjustments["Other Contract Deductions"] = matched

            for label, adjs in adjustments.items():
                for adj in adjs:
                    data.setdefault(label, {})
                    data[label].setdefault(adj.debit_account_id.id, {})
                    data[label].setdefault(adj.credit_account_id.id, {})
                    analytic_account_id = adj.analytic_account_id.id or payslip.contract_id.analytic_account_id.id
                    data[label][adj.debit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                    data[label][adj.credit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                    data[label][adj.debit_account_id.id][analytic_account_id]["debit"] += adj.amount
                    data[label][adj.credit_account_id.id][analytic_account_id]["credit"] += adj.amount
            
            # CONTRIBUTIONS
            contribs = payslip.contract_id.contribution_ids.filtered(
                lambda c: all([c.emp_debit_account_id, c.emp_credit_account_id]))
            label = "Employee Contributions"
            for contrib in contribs:
                data.setdefault(label, {})
                data[label].setdefault(contrib.emp_debit_account_id.id, {})
                data[label].setdefault(contrib.emp_credit_account_id.id, {})
                analytic_account_id = contrib.emp_analytic_account_id.id or payslip.contract_id.analytic_account_id.id
                data[label][contrib.emp_debit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][contrib.emp_credit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][contrib.emp_debit_account_id.id][analytic_account_id]["debit"] += contrib.employee_amount
                data[label][contrib.emp_credit_account_id.id][analytic_account_id]["credit"] += contrib.employee_amount
            contribs = payslip.contract_id.contribution_ids.filtered(
                lambda c: all([c.comp_debit_account_id, c.comp_credit_account_id]))
            label = "Company Contributions"
            for contrib in contribs:
                data.setdefault(label, {})
                data[label].setdefault(contrib.comp_debit_account_id.id, {})
                data[label].setdefault(contrib.comp_credit_account_id.id, {})
                analytic_account_id = contrib.comp_analytic_account_id.id or payslip.contract_id.analytic_account_id.id
                data[label][contrib.comp_debit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][contrib.comp_credit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][contrib.comp_debit_account_id.id][analytic_account_id]["debit"] += contrib.company_amount
                data[label][contrib.comp_credit_account_id.id][analytic_account_id]["credit"] += contrib.company_amount
            
            # LOANS
            payments = payslip.loan_payment_ids.filtered(
                lambda p: all([p.loan_id.debit_account_id, p.loan_id.credit_account_id]))
            for payment in payments:
                label = "Loan Payment: " + payment.loan_id.name
                data.setdefault(label, {})
                data[label].setdefault(payment.loan_id.debit_account_id.id, {})
                data[label].setdefault(payment.loan_id.credit_account_id.id, {})
                analytic_account_id = payment.loan_id.analytic_account_id.id
                data[label][payment.loan_id.debit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][payment.loan_id.credit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][payment.loan_id.debit_account_id.id][analytic_account_id]["debit"] += payment.amount
                data[label][payment.loan_id.credit_account_id.id][analytic_account_id]["credit"] += payment.amount
            
            # SAVINGS
            payments = payslip.savings_payment_ids.filtered(
                lambda p: all([p.savings_id.debit_account_id, p.savings_id.credit_account_id]))
            for payment in payments:
                label = "Savings Payment: " + payment.savings_id.name
                data.setdefault(label, {})
                data[label].setdefault(payment.savings_id.debit_account_id.id, {})
                data[label].setdefault(payment.savings_id.credit_account_id.id, {})
                analytic_account_id = payment.savings_id.analytic_account_id.id
                data[label][payment.savings_id.debit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][payment.savings_id.credit_account_id.id].setdefault(analytic_account_id, {"debit": 0.0, "credit": 0.0})
                data[label][payment.savings_id.debit_account_id.id][analytic_account_id]["debit"] += payment.amount
                data[label][payment.savings_id.credit_account_id.id][analytic_account_id]["credit"] += payment.amount

            line_ids = []
            for label, accounts in data.items():
                for account_id, analytic_accounts in accounts.items():
                    for analytic_account_id, amounts in analytic_accounts.items():
                        line_ids.append((0, 0, {
                            "move_id": payslip.move_id.id,
                            "account_id": account_id,
                            "name": label,
                            "analytic_account_id": analytic_account_id,
                            "debit": amounts["credit"] if payslip.credit_note else amounts["debit"],
                            "credit": amounts["debit"] if payslip.credit_note else amounts["credit"],
                        }))
            payslip.move_id.write({"line_ids": line_ids})
        return res