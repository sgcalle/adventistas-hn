odoo.define("pos_wallet.payment_screen", function (require) {
    "use strict";

    const {ProductListWidget, PaymentScreenWidget} = require('point_of_sale.screens');
    const {PosWalletPaymentScreenComponent} = require('pos_wallet.owl.components');

    // Append customer screen to main screen
    ProductListWidget.include({
        init: function () {
            this._super.apply(this, arguments);
            this.posWalletPaymentScreen = new PosWalletPaymentScreenComponent(null, {
                pos: this.pos,
            });
        },

        renderElement: function () {
            this._super.apply(this, arguments);
            this.renderPosWalletPaymentScreen();
        },

        show: function () {
            this._super.apply(this, arguments);
            this.renderPosWalletPaymentScreen();
        },

        renderPosWalletPaymentScreen: function () {
            if (this.posWalletPaymentScreen) {

                this.posWalletPaymentScreen.unmount();
                // if (this.posWalletPaymentScreen.__owl__.isMounted) {
                // }

                if (this.pos.get_client()) {
                    this.posWalletPaymentScreen.trigger('show', false);
                    this.posWalletPaymentScreen.mount(this.el).catch(console.error);
                }
            }
        }
    })

    PaymentScreenWidget.include({
        payment_input: function () {
            const paymentline = this.pos.get_order().selected_paymentline;
            if (paymentline.payment_method.wallet_category_id) {
                return;
            }
            this._super.apply(this, arguments);
        }
    })

});