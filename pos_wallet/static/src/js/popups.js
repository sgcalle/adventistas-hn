odoo.define('pos_wallet.popups', function (require) {

    const PopupWidget = require('point_of_sale.popups');
    const gui = require('point_of_sale.gui');
    const _t = require('web.core')._t;

    const LoadWalletPopup = PopupWidget.extend({
        events: _.extend({}, PopupWidget.prototype.events, {
            'focusout .js_wallet_amount': '_validateForm',
            'submit .js_load_wallet_popup_form': '_onSubmitLoadWalletForm',
        }),

        template: 'PosWalletLoadWalletForm',

        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.options.wallets = this.pos.config.wallet_category_ids;
        },

        /**
         * @private
         */
        _validateForm: function () {
            let isInvalid = false;

            isInvalid |= this._isInvalidWalletAmountInput();

            const btnSubmit = this.el.querySelector('.js_btn_submit_load_wallet');

            btnSubmit.disabled = isInvalid;
            return !isInvalid;
        },

        /**
         * @private
         */
        _isInvalidWalletAmountInput: function () {
            const jsWalletAmountInput = this.el.querySelector('input.js_wallet_amount');
            let isInvalid = false;

            if (jsWalletAmountInput) {
                if (!jsWalletAmountInput.value.match(/^\d*\.?\d*$/)) {
                    isInvalid = true;
                    const errorMessage = _t("Wallet amount is not a valid number");
                    jsWalletAmountInput.setCustomValidity(errorMessage);
                } else {
                    const walletAmountInputNumberValue = parseFloat(jsWalletAmountInput.value);
                    jsWalletAmountInput.value = walletAmountInputNumberValue.toFixed(2);
                }

            } else {
                isInvalid = true;
            }

            if (!isInvalid) {
                jsWalletAmountInput.setCustomValidity('');
            }

            return isInvalid
        },

        /**
         * @param {Event} event
         * @private
         */
        _onSubmitLoadWalletForm: function (event) {
            event.preventDefault();
            this.gui.close_popup();

            if (this._validateForm()) {
                const walletLoad = this.pos.load_wallet({
                    partner_id: this.pos.get_client().id,
                    wallet_category_id: parseInt(this.$el.find('.js_wallet_category').val()),
                    payment_method_id: parseInt(this.$el.find('.js_payment_method').val()),
                    amount: parseFloat(this.$el.find('.js_wallet_amount').val()),
                })
                this.gui.show_screen('walletLoadReceipt', {walletLoad: walletLoad});
            }
        }
    });
    gui.define_popup({name: 'posPrLoadWallet', widget: LoadWalletPopup});

    return {
        PopupWidget
    }
});