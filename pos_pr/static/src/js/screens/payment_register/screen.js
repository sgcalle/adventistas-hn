odoo.define("pos_pr.payment_register.screen", function (require) {

    const screens = require("point_of_sale.screens");
    const gui = require("point_of_sale.gui");
    const {PosPRScreen} = require('pos_pr.owl.components');
    // Invoices screen
    const PosPosPRWidget = screens.ScreenWidget.extend({

        events: {
            'click .back': '_go_to_back_screen',
        },

        back_screen: 'products',
        template: 'InvoicesLineWidget',

        /**
         * @override
         */
        init: function (options) {
            this._super.apply(this, arguments);
            this.pos.payment_register = this;
            this.invoicePaymentRegisterScreen = new PosPRScreen(null, {
                pos: this.pos,
                paymentRegister: this,
            });
        },

        /**
         * @override
         */
        renderElement: function () {
            this._super.apply(this, arguments);
            this.invoicePaymentRegisterScreen.mount(this.el.querySelector('#js_pos_payment_register_screen'));
        },

        /**
         * @override
         */
        show: function (reload) {
            this._super(); // We need to check if the user has selected a customer
            if (this.pos.get_client()) {
                this.invoicePaymentRegisterScreen.state.partner = this.pos.get_client();
            }
        },
        /**
         * @private
         */
        _go_to_back_screen: function () {
            this.gui.show_screen(this.back_screen);
        },
    });

    gui.define_screen({name: 'pos_invoice_payment_register_widget', widget: PosPosPRWidget});

    return PosPosPRWidget;
});
