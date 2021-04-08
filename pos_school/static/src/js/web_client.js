odoo.define('pos', require => {
    "use strict";

    const models = require('point_of_sale.models');

    const session = require('web.session');
    const Session = require('web.Session');

    const AbstractWebClient = require('web.WebClient')
    const utils = require('web.utils');
    const dom = require('web.dom');

    const _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        after_load_server_data: function() {
            const res = _super_posmodel.after_load_server_data.call(this);

            console.log(this.config.school_code_ids);
            console.log('After this loaded');
            
            session.user_context.allowed_school_code_ids = this.config.school_code_ids;

            return res;
        }
    });
});