odoo.define("pos_pr.load_data.account_payment_methodss", function (require) {

    const models = require("point_of_sale.models");
    const PosDB = require("point_of_sale.DB");

    PosDB.include({
        init: function (options) {
            this._super(options);
            this.account_payment_methods = [];
            this.account_payment_method_by_id = {};
        },

        add_account_payment_methods: function (accountPaymentMethods) {
            this.accountPaymentMethods = accountPaymentMethods;
            let self = this;
            _.each(accountPaymentMethods, function (accountPaymentMethod) {
                self.account_payment_method_by_id[accountPaymentMethod.id] = accountPaymentMethod;
            });
        },

    });

    // Load payment journals
    models.load_models([
        {
            model: "account.payment.method",
            fields: ["name"],
            domain: [
                ["payment_type", "=", "inbound"]
            ],
            loaded: function (self, accountPaymentMethods) {
                self.db.add_account_payment_methods(accountPaymentMethods);
            }
        }
    ]);

    models.load_models([
        {
            model: "pos.payment.method",
            fields: ["id", "name"],
            domain: [
                ["is_pos_pr_discount", "=", true]
            ],
            loaded: function (self, posPaymentMethods) {
                if (posPaymentMethods && posPaymentMethods.length > 0) {
                    self.db.discount_payment_method = posPaymentMethods[0];
                }
            }
        }
    ]);
});
