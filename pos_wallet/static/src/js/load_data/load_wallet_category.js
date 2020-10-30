odoo.define("pos_wallet.load_wallet_category", function (require) {

    const models = require("point_of_sale.models")
    const PosDB = require("point_of_sale.DB")

    models.load_fields('pos.payment.method', ['wallet_category_id'])

    PosDB.include({
        init: function (options) {
            this._super(options);
            this.wallet_payment_methods = [];
            this.payment_method_by_wallet_id = {};
        },

        add_wallet_payment_methods: function (payment_methods) {
            this.wallet_payment_methods = payment_methods;
            let self = this;
             _.each(payment_methods, function (payment_method) {
                self.payment_method_by_wallet_id[payment_method.wallet_category_id[0]] = payment_method;
            });
        }
    });

    // Load wallets payment methods
    models.load_models([
        {
            model: 'pos.payment.method',
            fields: ['name', 'wallet_category_id'],


            domain: function(self, tmp) {
                return [
                    ['wallet_category_id', '!=', false],
                    // ['id', 'in', tmp.payment_method_ids]
                ];
            },
            loaded: function (self, payment_methods) {
                self.db.add_wallet_payment_methods(payment_methods);
            }
        }
    ]);


})