odoo.define("pos_pr.load_data.journals", function (require) {

    const models = require("point_of_sale.models")
    const PosDB = require("point_of_sale.DB")

    // Load payment journals
    models.load_models([
        {
            model: "account.journal",
            fields: ["display_name", "inbound_payment_method_ids"],
            domain: [],
            loaded: function (self, journals) {
                self.db.add_journals(journals);
            }
        }
    ]);

    PosDB.include({
        init: function (options) {
            this._super(options);
            this.journal = [];
            this.journal_by_id = {};
        },

        add_journals: function (add_journals) {
            this.journals = add_journals;
            let self = this;
             _.each(add_journals, function (journal) {
                self.journal_by_id[journal.id] = journal;
            });
        }
    });

})