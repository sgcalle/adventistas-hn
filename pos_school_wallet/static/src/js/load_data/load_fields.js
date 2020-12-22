odoo.define('pos_wallet_school.load_fields', require => {

    const models = require('point_of_sale.models');
    models.load_fields('res.partner', ['related_families_by_inv_address_ids']);
});