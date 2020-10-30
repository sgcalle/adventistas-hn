odoo.define("pos_wallet.load_partner_fields", function (require) {
    "use strict";

    const PosDB = require('point_of_sale.DB');
    const models = require('point_of_sale.models');
    models.load_fields('res.partner', ['json_dict_wallet_amounts']);

    PosDB.include({
        add_partners: function (partners) {
            let updated_count = this._super(partners);

            _.each(partners, partner => {
                partner.json_dict_wallet_amounts = JSON.parse(partner.json_dict_wallet_amounts)
            })

            return updated_count;
        }
    })

});