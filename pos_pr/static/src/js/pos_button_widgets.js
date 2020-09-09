odoo.define('pos_pr.buttons', function (require) {
    'use strict';

    const screens = require("point_of_sale.screens");
    require("pos_pr.payment_register.screen");

    let BtnRegisterPayment = screens.ActionButtonWidget.extend({
        template: "BtnRegisterPayment",

        /**
         * Inherited method: this fire up when the button is clicked
         */
        button_click: function () {
            this.goToRegisterPaymentScreen();
        },

        goToRegisterPaymentScreen: function () {
            // var self = this;
            this.gui.show_screen("pos_invoice_payment_register_widget");
        },

    });

    screens.define_action_button({'name': 'goToRegisterPaymentScreen', 'widget': BtnRegisterPayment});
    return {
        "BtnRegisterPayment": BtnRegisterPayment
    };
});
