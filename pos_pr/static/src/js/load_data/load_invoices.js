odoo.define("pos_pr.load_data.invoices", function (require) {

    const models = require('point_of_sale.models');
    const PosDB = require("point_of_sale.DB");

    PosDB.include({
        init: function (options) {
            this._super(options);
            this.due_invoices = [];
            this.due_invoices_by_id = {};
        },

        add_due_invoices: function (invoices) {
            const self = this;

            _.each(invoices, function (invoice) {

                invoice.amount_residual -= invoice.pos_pr_paid_amount;

                invoice.expected_final_due = invoice.amount_residual;
                invoice.original_surcharge = invoice.surcharge_amount;
                invoice.session_payment = 0;
                self.due_invoices.push(invoice);
                self.due_invoices_by_id[invoice.id] = invoice;
            });
        },
    });

    models.load_models([
        {
            model: "account.move",
            fields: ["name", "journal_id", "partner_id", "invoice_date", "invoice_date_due", "amount_total",
                     "amount_residual", "surcharge_invoice_id", "is_overdue", "surcharge_amount", "pos_pr_paid_amount"],
            domain: [
                ["type", "=", "out_invoice"],
                ["invoice_payment_state", "!=", "paid"],
                ["state", "=", "posted"],
            ],
            order: [{name: 'invoice_date_due', asc: true}],//, function (name) { return {name: name}; }),
            loaded: function (self, invoices) {
                self.db.add_due_invoices(invoices);
            }
        }
    ]);
})