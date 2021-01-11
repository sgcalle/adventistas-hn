odoo.define("pos_pr.load_data.account_payment_methodss", function (require) {

    const models = require("point_of_sale.models");
    const PosDB = require("point_of_sale.DB");

    // Load payment journals
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
