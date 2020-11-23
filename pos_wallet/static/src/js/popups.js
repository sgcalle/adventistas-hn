odoo.define('pos_wallet.popups', function (require) {

    const PopupWidget = require('point_of_sale.popups');
    const gui = require('point_of_sale.gui');
    const _t = require('web.core')._t;

    const {Component, useState} = owl;
    const {useRef} = owl.hooks;
    const {verifyInputNumber} = require('eduweb_utils.numbers');

    class PosWalletLoadWalletComponent extends Component {
        static props = ['walletPopup', 'pos']

        walletAmount = useRef("walletAmount");
        state = useState({
            paymentAmount: 0,
            walletCategory: 0,
            paymentMethod: 0,
            currentPartner: {},
        });

        patched() {
            super.patched();
        }

        triggerInputAction(event) {
            const decimals = ((window.posmodel && window.posmodel.currency) ? window.posmodel.currency.decimals : 2) || 2;
            let paymentAmount = verifyInputNumber(this.walletAmount.el, decimals);
            this.state.paymentAmount = paymentAmount;
            event.currentTarget.value = paymentAmount;
        }

        get formIsValid() {
            return this.state.paymentAmount && this.state.walletCategory && this.state.paymentMethod
        }

    }

    const LoadWalletPopup = PopupWidget.extend({
        events: _.extend({}, PopupWidget.prototype.events, {
            // 'focusout .js_wallet_amount': '_validateForm',
            'submit .js_load_wallet_popup_form': '_onSubmitLoadWalletForm',
        }),

        template: 'PosWalletLoadWalletForm',

        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.options.wallets = this.pos.config.wallet_category_ids;
            this.posWalletLoadWalletComponent = new PosWalletLoadWalletComponent(null, {walletPopup: this, pos: this.pos});
        },

        renderElement: function () {
            this._super.apply(this, arguments);

            const owlComponentToMountEl = this.el.querySelector('.js_load_wallet_owl_component');
            this.posWalletLoadWalletComponent.mount(owlComponentToMountEl);

        },

        show: function () {
            this._super.apply(this, arguments);
            this.posWalletLoadWalletComponent.state.currentPartner = this.pos.get_client();
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

        _build_load_wallet_options: function () {
            return  {
                partner_id: this.pos.get_client().id,
                wallet_category_id: parseInt(this.$el.find('.js_wallet_category').val()),
                payment_method_id: parseInt(this.$el.find('.js_payment_method').val()),
                amount: parseFloat(this.$el.find('.js_wallet_amount').val()),
            }
        },

        /**
         * @param {Event} event
         * @private
         */
        _onSubmitLoadWalletForm: function (event) {
            event.preventDefault();
            this.gui.close_popup();

            if (this._validateForm()) {
                const walletLoad = this.pos.load_wallet(this._build_load_wallet_options());
                this.gui.show_screen('walletLoadReceipt', {walletLoad: walletLoad});
            }
        }
    });
    gui.define_popup({name: 'posPrLoadWallet', widget: LoadWalletPopup});

    return {
        LoadWalletPopup,
        PosWalletLoadWalletComponent
    }
});