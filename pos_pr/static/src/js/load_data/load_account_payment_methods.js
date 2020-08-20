odoo.define("pos_pr.load_data.account_payment_methodss", function (require) {

    const models = require("point_of_sale.models")
    const PosDB = require("point_of_sale.DB")

    PosDB.include({
        init: function (options) {
            this._super(options);
            this.account_payment_methods = [];
            this.account_payment_method_by_id = {};
        },

        add_account_payment_methods: function (account_payment_methods) {
            this.account_payment_methods = account_payment_methods;
            let self = this;
             _.each(account_payment_methods, function (account_payment_method) {
                self.account_payment_method_by_id[account_payment_method.id] = account_payment_method;
            });
        }
    });

    // Load payment journals
    models.load_models([
        {
            model: "account.payment.method",
            fields: ["name"],
            domain: [
                ["payment_type", "=", "inbound"]
            ],
            loaded: function (self, account_payment_methods) {
                self.db.add_account_payment_methods(account_payment_methods);
            }
        }
    ]);


})