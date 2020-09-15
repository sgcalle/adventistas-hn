odoo.define("pos_pr.payment_register.components.dashboard.screen", function (require) {

    const PosBaseWidget = require('point_of_sale.BaseWidget');
    const NumberInput = require('eduweb_utils.NumberInput');
    const core = require("web.core");
    const _t = core._t;

    const PaymentListWidget = PosBaseWidget.extend({
        template: 'PaymentRegister.components.Dashboard.PaymentList',
        events: {
            'input .input-payment-method input': '_trigger_parent_update_amount_event',
            'keydown .input-payment-method input': '_save_previous_value',
            'change .js_radio_discount_type': '_toggle_discount_percentage_input',
            'input #discount_percentage': '_compute_discount_with_percentage',
            'input input[name="input_payment_discount"]': '_update_discount_amount',
            'keydown input[name="input_payment_discount"]': '_save_previous_value',
        },


        /**
         * @override
         */
        renderElement: function () {
            this._super.apply(this, arguments);
            this.$el.find('input.numeric-input').each((index, input) => {
                NumberInput(input, {'decimal_limit': 2});
            });

            const isAnInvoiceSelected = !!this.invoice;
            this.$el.find('.input-payment-discount').toggle(isAnInvoiceSelected);
            if (isAnInvoiceSelected) {
                const inputPaymentDiscount = this.el.querySelector('input[name="input_payment_discount"]');
                inputPaymentDiscount.value = this.invoice.discount || 0;
                NumberInput(inputPaymentDiscount, {'decimal_limit': 2});
            }
        },

        /**
         * Update payment amounts
         * @private
         */
        _trigger_parent_update_amount_event: function (event) {
            this.getParent().trigger('payment:update_amount', {input: event.currentTarget});
        },

        /**
         * Hides the percentage input dynamically
         * @private
         */
        _toggle_discount_percentage_input: function () {
            const $percentageRadio = this.$el.find('#discount_type-radio-percentage');
            const targets = $($percentageRadio.data('target'));
            targets.toggleClass('oe_hidden', !$percentageRadio.prop('checked'));
        },

        /**
         * Compute the discount using the percentage
         * @private
         */
        _compute_discount_with_percentage: function (event) {
            const inputPercentage = event.currentTarget;
            const $totalDiscountInput = this.$el.find(inputPercentage.dataset.target);
            const invoiceTotalDue = parseFloat(this.invoice.amount_residual);
            const percentage = (parseFloat(inputPercentage.value) || 0) / 100;

            const previousAmount = parseFloat($totalDiscountInput.val()) || 0;
            $totalDiscountInput.data('oldValue', previousAmount);
            $totalDiscountInput.val((invoiceTotalDue * percentage).toFixed(2));
            $totalDiscountInput.trigger('input');
        },

        /**
         * Update the current invoice's discount on parent widget
         * @private
         */
        _update_discount_amount: function (event) {
            if (this.invoice) {

                const inputPaymentDiscount = event.currentTarget;
                const amount = parseFloat(inputPaymentDiscount.value) || 0;

                const oldAmount = parseFloat(inputPaymentDiscount.dataset.oldValue) || 0;

                if (this.invoice.expected_final_due + oldAmount - amount < 0) {
                    let selectionPositionStart = inputPaymentDiscount.selectionStart;
                    let selectionPositionEnd = inputPaymentDiscount.selectionEnd;

                    inputPaymentDiscount.value = inputPaymentDiscount.dataset.oldValue;

                    inputPaymentDiscount.setSelectionRange(selectionPositionStart, selectionPositionEnd);
                    return;
                }

                this.getParent().paymentRegisterWidget.trigger('discount:update', {
                    'invoice': this.invoice,
                    'amount': amount,
                });



            } else {
                throw new Error('You need to provide a invoice to PaymentListWidget to use this method');
            }
        },

        /**
         * Save in a data tag the previous value of the input
         * @private
         */
        _save_previous_value: function (event) {
            const inputEl = event.currentTarget;
            inputEl.dataset.oldValue = inputEl.value;
        },
    });

    const InvoiceDetailsWidget = PosBaseWidget.extend({
        template: 'PaymentRegister.components.Dashboard.InvoiceDetails',
    });


    const DashboardScreenWidget = PosBaseWidget.extend({
        template: 'PaymentRegister.components.Dashboard',

        custom_events: {
            'payment:update_amount': '_update_payment_amounts',
            'surcharge:toggle_elements': '_toggle_surcharge_elements',
        },

        /**
         * @override
         */
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.paymentListWidget = new PaymentListWidget(this, options);
            this.invoiceDetailsWidget = new InvoiceDetailsWidget(this, options);
            this.paymentRegisterWidget = this.getParent();
        },

        /**
         * @override
         */
        renderElement: function () {
            this._super.apply(this, arguments);

            this.paymentListWidget.payment_methods_amounts = this.getParent()._get_payment_method_amounts(null);
            this.paymentListWidget.renderElement();
            this.invoiceDetailsWidget.renderElement();

            this.$el.find('.invoice-details-contents')
                .append(this.invoiceDetailsWidget.el)
                .append(this.paymentListWidget.el);
        },

        /**
         * @public
         */
        updateDraw: function () {
            this.invoiceDetailsWidget.invoice = this.invoice;
            this.invoiceDetailsWidget.renderElement();

            this.paymentListWidget.payment_methods_amounts = this.getParent()._get_payment_method_amounts(this.invoice);
            this.paymentListWidget.invoice = this.invoice;
            this.paymentListWidget.renderElement();
            this._toggle_surcharge_elements();
        },

        /**
         * @private
         */
        _update_payment_amounts: function (event) {
            const paymentMethodInput = event.input;
            if (paymentMethodInput) {
                let amount = parseFloat(paymentMethodInput.value);
                const paymentMethodId = parseInt(paymentMethodInput.closest('tr').dataset.id);
                const oldAmount = parseFloat(paymentMethodInput.dataset.oldValue) || 0;

                if (this.invoice && this.invoice.expected_final_due + oldAmount - amount < 0) {
                    let selectionPositionStart = paymentMethodInput.selectionStart;
                    let selectionPositionEnd = paymentMethodInput.selectionEnd;

                    paymentMethodInput.value = paymentMethodInput.dataset.oldValue;

                    paymentMethodInput.setSelectionRange(selectionPositionStart, selectionPositionEnd);
                    return;
                }

                this.paymentRegisterWidget._update_invoice_payment_amount(this.invoice, paymentMethodId, amount);
            }
        },

        /**
         * @private
         */
        _toggle_surcharge_elements: function () {
            if (this.paymentRegisterWidget.partner_id) {
                let isSurchargePaid = this.paymentRegisterWidget.surcharge_amount - (this.paymentRegisterWidget.free_of_surcharge[this.paymentRegisterWidget.partner_id.id] || 0) === 0;
                this.getParent().trigger('surcharge:toggle_elements', {'is_surcharge_paid': isSurchargePaid});
                if (!isSurchargePaid) {
                    this.getParent().render_message(_t("You need pay the surcharge first"));
                }
            }
        }
    });

    return DashboardScreenWidget;
});
