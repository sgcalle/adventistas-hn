odoo.define("pos_pr.payment_register.screen", function (require) {

    const screens = require("point_of_sale.screens");

    const gui = require("point_of_sale.gui");
    const core = require("web.core");
    const registerModels = require("pos_pr.models");
    const tools = require('pos_pr.tools');
    const NumberInput = require('eduweb_utils.NumberInput');

    const PaymentRegisterInvoiceListScreen = require("pos_pr.payment_register.components.invoice_list.screen");
    const PaymentRegisterDashScreen = require("pos_pr.payment_register.components.dashboard.screen");
    const QWeb = core.qweb;

    // Invoices screen
    const PosInvoicePaymentRegisterWidget = screens.ScreenWidget.extend({

        events: {
            'click .back': '_go_to_back_screen',
            'click .invoice-list__content-line': '_toggle_invoice_selection',
            'click .apply-payments': '_apply_general_payment_to_invoices',
            'click .validate-payments': 'validate_payment',
            'click .pay-surcharge': 'pay_surcharge',
            'click .cancel-surcharge': 'cancel_surcharge',
        },

        custom_events: {
            'surcharge:toggle_elements': '_toggle_surcharge_elements',
            'discount:update': '_update_discount_amount',
            'payment_amounts:update': '_redraw_amounts',
        },

        back_screen: 'products',
        template: 'InvoicesLineWidget',

        /**
         * @override
         */
        init: function (options) {
            this._super.apply(this, arguments);
            this.pos.payment_register = this;

            this.global_invoice_payments_by_partner_id = {};
            this.free_of_surcharge = {};
            this.invoiceListScreen = new PaymentRegisterInvoiceListScreen(this, {});
            this.dashboardScreen = new PaymentRegisterDashScreen(this, {});
        },

        /**
         * @override
         */
        renderElement: function () {
            this._super.apply(this, arguments);

            this.invoiceListScreen.renderElement();
            this.dashboardScreen.renderElement();

            this.$el.find('.screen-right').append(this.dashboardScreen.el);
            this.$el.find('.js_invoice_list_container').append(this.invoiceListScreen.$el);
        },

        /**
         * @override
         */
        show: function (reload) {
            this._super(); // We need to check if the user has selected a customer
            let self = this;

            if (!reload) {
                this.reload_pos_data();
            }

            this._clear_register_dashboard();

            if (this.pos.get('cashier').role !== 'manager') {
                this.$el.find('.js-global-free-surcharge').addClass("oe_hidden");
            } else {
                this._show_free_surcharge_input();
            }
            if (this.partner_id) {
                this._render_invoices();
                this._redraw_amounts();

                // Total surcharge in input
                let jsGlobalTotalSurchargeInput = this.el.querySelector(".js-global-total-surcharge-input");
                NumberInput(jsGlobalTotalSurchargeInput, {decimal_limit: 2});

                // Free of surcharge
                let jsGlobalFreeSurchargeInput = this.el.querySelector(".js-global-free-surcharge-input");
                jsGlobalFreeSurchargeInput.value = (this.free_of_surcharge[this.partner_id.id] || 0) || 0;
                NumberInput(jsGlobalFreeSurchargeInput, {decimal_limit: 2});
                jsGlobalFreeSurchargeInput.addEventListener("input", function () {
                    self.free_of_surcharge[self.partner_id.id] = parseFloat(jsGlobalFreeSurchargeInput.value);
                });


                this.dashboardScreen.trigger('surcharge:toggle_elements');

                // Discount
                const inputPaymentDiscount = this.el.querySelector("input[name='input_payment_discount']");
                NumberInput(inputPaymentDiscount, {decimal_limit: 2});
            }
        },

        /**
         * @private
         */
        _show_free_surcharge_input: function () {
            let self = this;
            let $globalFreeSurchargeTr = this.$el.find('.js-global-free-surcharge');
            $globalFreeSurchargeTr.removeClass("oe_hidden");
            let $globalFreeSurchargeInput = $globalFreeSurchargeTr.find(".js-global-free-surcharge-input");
            $globalFreeSurchargeInput.on("input", function () {
                let freeOfSurcharge = parseFloat($globalFreeSurchargeInput.val());
                let surchargeComputed = isNaN(self.surcharge_amount - freeOfSurcharge) ? self.surcharge_amount : self.surcharge_amount - freeOfSurcharge;
                self.$el.find(".js-global-total-surcharge input").val(surchargeComputed.toFixed(2));
            });
        },

        /**
         * Render a message in the invoice list section
         * @public
         * @param message
         */
        render_message: function (message) {
            this.invoiceListScreen.render_message(message);
        },

        /**
         * @private
         */
        _clear_register_dashboard: function () {
            this.$el.find("table.invoice-list tbody.invoice-list__content").empty();
            this._draw_payment_dashboard();

            // this.$el.find(".invoice-details-contents").empty();
            this.$el.find(".background-message").remove();
        },

        /**
         * @private
         */
        _render_invoices: function () {
            let invoiceIds = this.pos.db.due_invoices.filter(invoice =>
                invoice.partner_id.id === this.partner_id.id && invoice.amount_residual > 0
            );
            this.invoice_ids = invoiceIds;
            this.invoiceListScreen.show(true);
            if (invoiceIds.length) {
                this._refresh_surcharge_values(invoiceIds);
            }
        },

        /**
         * @private
         */
        _refresh_surcharge_values: function () {
            let self = this;
            let totalSurcharge = 0;

            _.each(this.invoice_ids, function (invoice) {
                let invoiceDueDate = new Date(invoice.invoice_date_due || invoice.invoice_date);
                let todayDate = new Date();
                todayDate.setHours(0, 0, 0, 0);
                if (invoiceDueDate < todayDate) {
                    totalSurcharge += invoice.surcharge_amount;
                } else if (invoiceDueDate.getTime() === todayDate.getTime()) {
                    totalSurcharge += invoice.surcharge_amount;
                }
            });

            this.surcharge_amount = parseFloat(totalSurcharge);
            self.$el.find(".js-global-total-surcharge input").val(totalSurcharge - (this.free_of_surcharge[this.partner_id.id] || 0));
            this.dashboardScreen.trigger('surcharge:toggle_elements');
        },

        /**
         * @private
         */
        _go_to_back_screen: function () {
            this.gui.show_screen(this.back_screen);
        },

        /**
         * @private
         */
        _toggle_invoice_selection: function (event) {
            if (this.surcharge_amount - (this.free_of_surcharge[this.partner_id.id] || 0) === 0) {
                let invoiceRow = event.currentTarget;

                this._toggle_select_class(invoiceRow);
                this._redraw_amounts();

                let invoice = this._get_invoice_by_html(invoiceRow);

                if (this.selected_invoice.id === invoice.id) {
                    this._deselect_invoice(invoice);
                } else {
                    this._select_invoice(invoice);
                }
            }
        },

        /**
         * @private
         */
        _toggle_select_class: function (invoice) {
            let isCurrentRowSelected = $(invoice).hasClass("invoice-list__content-line--selected");
            this.$el.find(".invoice-list__content-line").removeClass("invoice-list__content-line--selected");
            if (!isCurrentRowSelected) {
                $(invoice).toggleClass("invoice-list__content-line--selected");
            }
        },

        /**
         * @private
         */
        _get_invoice_by_html: function (invoiceHtmlRow) {
            let invoiceId = parseInt(invoiceHtmlRow.dataset["id"]);
            return this.pos.db.due_invoices_by_id[invoiceId];
        },

        /**
         * @private
         */
        _deselect_invoice: function () {
            this.selected_invoice = {};
            this.$el.find(".apply-payments").show();
            this._draw_payment_dashboard();
        },

        /**
         * @private
         */
        _select_invoice: function (invoice) {
            this.selected_invoice = invoice;
            this._draw_selected_invoice_payments();
        },

        /**
         * @private
         */
        _draw_selected_invoice_payments: function () {
            this.$el.find(".apply-payments").hide();
            this._draw_payment_dashboard(this.selected_invoice);
        },

        /**
         * @private
         */
        _draw_payment_dashboard: function (invoice) {
            this.dashboardScreen.invoice = invoice;
            this.dashboardScreen.updateDraw();
        },

        /**
         * @private
         */
        _update_invoice_payment_amount(invoiceId, paymentMethodId, amount) {

            if (typeof (invoiceId) == 'object') {
                invoiceId = invoiceId.id;
            }
            let globalInvoicePayments = this._get_value_with_default(this.global_invoice_payments_by_partner_id, this.partner_id.id, {});
            let invoicePaymentMethods = this._get_value_with_default(globalInvoicePayments, invoiceId, {});

            let lookingPaymentAmountObject = invoiceId ? invoicePaymentMethods : this.general_payments;

            lookingPaymentAmountObject[paymentMethodId] = tools.cast_to_float(amount);

            if (invoiceId) {
                let invoice = this.pos.db.due_invoices_by_id[invoiceId];
                invoice.expected_final_due = invoice.amount_residual
                    - tools.sum_object_properties(this._get_payment_method_amounts(invoice))
                    - invoice.discount_amount;
            }
            this.trigger("payment_amounts:update");
        },

        /**
         * @private
         */
        _get_value_with_default: function (object, key, defaultValue) {
            object = object || {};
            if (!Object.prototype.hasOwnProperty.call(object, key)) {
                object[key] = defaultValue;
            }
            return object[key];
        },

        /**
         * @private
         */
        _redraw_amounts: function () {
            this._render_global_payment_amounts();
            this._refresh_invoice_lines_values();
        },

        /**
         * @private
         */
        _refresh_invoice_lines_values: function () {
            let self = this;
            if (this.invoice_ids) {
                _.each(this.invoice_ids, (invoice) => {
                    let $invoiceRow = self.$el.find(_.str.sprintf('.invoice-list__content-line[data-id=%s]', invoice.id));
                    $invoiceRow.find(".js-expected-final-due").text(invoice.expected_final_due.toFixed(2));
                });
            }
        },

        /**
         * @private
         */
        _render_global_payment_amounts: function () {

            let total = 0;
            let totalDue = tools.sum_object_properties(this.invoice_ids.map((invoice) => invoice.amount_residual));

            let globalInvoicePayments = this.global_invoice_payments_by_partner_id[this.partner_id.id];
            if (globalInvoicePayments) {
                total = tools.sum_object_properties(Object.values(globalInvoicePayments).map(tools.sum_object_properties));
            }

            this.total_amount = total;
            this.total_due = totalDue;

            this.$el.find('.js-global-total-paid').text(total.toFixed(2));

            let globalTotalDue = (totalDue - total).toFixed(2);

            this.$el.find('.js-global-total-due').text(globalTotalDue);
            this.dashboardScreen.trigger('surcharge:toggle_elements');
        },

        /**
         * @private
         */
        _apply_general_payment_to_invoices: function () {
            if (this.invoice_ids) {
                let globalInvoicePayments = this._get_value_with_default(this.global_invoice_payments_by_partner_id, this.partner_id.id, {});
                let dueInvoices = _.filter(this.invoice_ids, (invoice) => invoice.expected_final_due > 0);
                _.each(dueInvoices, (invoiceId) => {
                    this._apply_general_payment_to_invoice(globalInvoicePayments, invoiceId);
                });
                this.show(true);
            }
        },

        /**
         * @private
         */
        _apply_general_payment_to_invoice: function (globalInvoicePayments, invoiceId) {
            let invoicePaymentMethods = this._get_value_with_default(globalInvoicePayments, invoiceId.id, {});
            let totalPaidToInvoice = 0;
            _.each(this.pos.payment_methods, (paymentMethodId) => {
                totalPaidToInvoice += this._try_to_apply_payment_to_invoice(paymentMethodId, invoiceId, invoicePaymentMethods);
            });
            totalPaidToInvoice += invoiceId.discount_amount || 0;
            invoiceId.expected_final_due = invoiceId.amount_residual - totalPaidToInvoice;
        },

        /**
         * @private
         */
        _try_to_apply_payment_to_invoice: function (paymentMethodId, invoiceId, invoicePaymentMethods) {
            let generalPay = this.general_payments[paymentMethodId.id];
            let amountToPay = Math.min(invoiceId.expected_final_due, generalPay);

            if (amountToPay > 0) {
                this.general_payments[paymentMethodId.id] -= amountToPay;
                this._update_invoice_payment_amount(invoiceId.id, paymentMethodId.id, (invoicePaymentMethods[paymentMethodId.id] || 0) + amountToPay);
            }
            return amountToPay;
        },

        /**
         * @private
         */
        _generate_surcharge: function () {
            let surcharge = new registerModels.SurchargeInvoice;
            surcharge.date = tools.format_date(new Date());
            surcharge.pos_session_id = this.pos.pos_session.id;
            surcharge.partner_id = this.partner_id.id;
            surcharge.free_of_surcharge = (this.free_of_surcharge[this.partner_id.id] || 0) || 0;

            let surchargePaymentInvoiceIds = this._clear_all_invoices_surcharge(surcharge);
            this._append_payments_to_surcharge(surcharge, surchargePaymentInvoiceIds);

            surcharge.amount = tools.sum_object_properties(surcharge.payment_ids.map(paymentId => paymentId.payment_amount));

            return surcharge;
        },

        /**
         * @private
         */
        _get_surcharge_pay_amount: function () {
            let surchargeTotal = this._get_surcharge_total();
            let paymentTotal = this._get_payment_total();

            return Math.min(surchargeTotal, paymentTotal);
        },

        /**
         * @private
         */
        _get_surcharge_total: function () {
            return parseFloat(this.el.querySelector(".js-global-total-surcharge-input").value);
        },

        /**
         * @private
         */
        _get_payment_total: function () {

            let amountTotal = 0;

            _.each(this.pos.payment_methods, paymentMethodId => {
                let $paymentTr = this.$el.find(".payment-method-list .input-payment-method[data-id='" + paymentMethodId.id + "']");
                let inputVal = parseFloat($paymentTr.find("input").val());
                amountTotal += inputVal || 0;
            });

            return parseFloat(amountTotal);
        },

        /**
         * @private
         */
        _get_invoice_details_qweb: function (invoice) {
            let invoiceDetails = QWeb.render('InvoiceDetails', {
                "widget": this,
                "move": invoice,
                "journal_by_id": this.pos.db.journal_by_id,
            });

            return $(invoiceDetails.trim());
        },

        /**
         * @private
         */
        _get_payment_method_qweb: function (invoice) {
            let paymentMethodsAmounts = this._get_payment_method_amounts(invoice);
            let paymentMethodQweb = QWeb.render('PaymentList', {
                "widget": this,
                "move": invoice,
                "payment_method_ids": this.pos.payment_methods,
                "payment_methods_amounts": paymentMethodsAmounts
            });
            return $(paymentMethodQweb.trim());
        },

        /**
         * @private
         */
        _get_payment_method_amounts: function (invoice) {
            let lookupInvoicePayments = this.general_payments;


            if (invoice) {
                let invoiceId = typeof invoice === 'object' ? invoice.id : invoice;
                let globalInvoicePayments = this._get_value_with_default(this.global_invoice_payments_by_partner_id, this.partner_id.id, {});
                lookupInvoicePayments = this._get_value_with_default(globalInvoicePayments, invoiceId, {});
            }

            let paymentAmounts = {};
            _.each(this.pos.payment_methods, (paymentMethod) => {
                paymentAmounts[paymentMethod.id] = this._get_value_with_default(lookupInvoicePayments, paymentMethod.id, 0.0);
            });
            return paymentAmounts;
        },

        /**
         * @private
         */
        _clear_all_invoices_surcharge: function (surchargeId) {
            let surchargePaymentInvoiceIds = {};

            let invoicePaymentsAmounts = Object.values(this._get_current_dashboard_payments()) || [];
            invoicePaymentsAmounts = Array.prototype.filter.call(invoicePaymentsAmounts, payment => payment.payment_amount > 0);
            let paymentMethodIndex = 0;

            let invoiceIdsWithSurcharge = this.invoice_ids.filter(invoice => invoice.surcharge_amount > 0);
            this.free_of_surcharge[this.partner_id.id] = this.free_of_surcharge[this.partner_id.id] || 0;
            if (invoicePaymentsAmounts.length > 0) {
                for (let invoice of invoiceIdsWithSurcharge) {

                    if (invoice.surcharge_amount <= 0 && paymentMethodIndex >= invoicePaymentsAmounts.length) {
                        break;
                    } else {
                        if (surchargeId.move_ids.indexOf(invoice.id) === -1) {
                            surchargeId.move_ids.push(invoice.id);
                        }
                    }

                    invoice.last_surcharge_amount = invoice.surcharge_amount;

                    if (this.free_of_surcharge[this.partner_id.id] > 0) {
                        let freeOfSurchargeAmount = Math.min(invoice.surcharge_amount, (this.free_of_surcharge[this.partner_id.id] || 0));
                        invoice.surcharge_amount -= freeOfSurchargeAmount;
                        this.free_of_surcharge[this.partner_id.id] -= freeOfSurchargeAmount;
                        this.surcharge_amount -= freeOfSurchargeAmount;
                    }

                    while (invoice.surcharge_amount > 0 && paymentMethodIndex < invoicePaymentsAmounts.length) {

                        let paymentId = invoicePaymentsAmounts[paymentMethodIndex];
                        let surchargeTotalPayment = surchargePaymentInvoiceIds[paymentId.payment_method_id] || 0;

                        let journalToPay = Math.min(invoice.surcharge_amount, paymentId.payment_amount);
                        paymentId.payment_amount -= journalToPay;

                        invoice.surcharge_amount -= journalToPay;
                        this.surcharge_amount -= journalToPay;
                        surchargeTotalPayment += journalToPay;

                        if (paymentId.payment_amount <= 0) {
                            paymentMethodIndex++;
                        }

                        this._update_invoice_payment_amount(undefined, paymentId.payment_method_id, paymentId.payment_amount);
                        surchargePaymentInvoiceIds[paymentId.payment_method_id] = surchargeTotalPayment;
                    }

                }
            }

            this.show(true);

            return surchargePaymentInvoiceIds;
        },

        /**
         * @private
         */
        _get_current_dashboard_payments: function () {
            let self = this;
            let payments = {};

            this.$el.find(".payment-method-list tr.input-payment-method").each((index, el) => {

                let paymentAmount = parseFloat(el.querySelector("input").value) || 0;
                let invoicePayment = new registerModels.InvoicePayment;

                invoicePayment.date = tools.format_date(new Date());
                invoicePayment.payment_amount = paymentAmount;
                invoicePayment.payment_method_id = parseInt(el.dataset.id);
                invoicePayment.pos_session_id = self.pos.pos_session.id;

                payments[invoicePayment.payment_method_id] = invoicePayment;

            });

            return payments;
        },

        /**
         * @private
         */
        _append_payments_to_surcharge: function (surchargeId, surchargePaymentInvoiceIds) {

            _.each(surchargePaymentInvoiceIds, (paymentAmount, paymentMethodId) => {
                let invoicePayment = new registerModels.InvoicePayment;

                invoicePayment.name = this.pos.generateNextPaymentNumber();
                invoicePayment.date = tools.format_date(new Date());
                invoicePayment.payment_amount = paymentAmount;
                invoicePayment.payment_method_id = this.pos.payment_methods_by_id[paymentMethodId];
                invoicePayment.pos_session_id = this.pos.pos_session.id;

                surchargeId.payment_ids.push(invoicePayment);
            });
        },

        /**
         * @public
         */
        pay_surcharge: function () {
            let surcharge = this._generate_surcharge();
            this.pos.gui.show_screen('surchargePaymentReceipt', {surcharge});
            // this.pos.synch_invoive_payment_and_surcharges([], [surcharge]);
            // this.show(true);
        },

        /**
         * @public
         */
        build_invoice_payments: function () {
            let invoicePaymentList = [];
            if (this.invoice_ids) {
                let self = this;
                _.each(this.invoice_ids, (invoice) => {
                    let invoicePaymentAmounts = this._get_payment_method_amounts(invoice);
                    _.each(this.pos.payment_methods, (paymentMethod) => {

                        let invoicePayment = new registerModels.InvoicePayment;

                        let invoicePaymentAmount = invoicePaymentAmounts[paymentMethod.id];
                        if (invoicePaymentAmount > 0) {

                            // Name is generated when the payment is created in odoo
                            invoicePayment.name = self.pos.generateNextPaymentNumber();
                            invoicePayment.date = tools.format_date(new Date());
                            invoicePayment.payment_amount = invoicePaymentAmounts[paymentMethod.id];
                            invoicePayment.payment_method_id = paymentMethod;
                            invoicePayment.move_id = invoice;
                            invoicePayment.pos_session_id = self.pos.pos_session.id;

                            invoicePaymentList.push(invoicePayment);

                        }
                    });

                    // Check if we have some discount
                    // We are going to pass the discount as an payment without payment method
                    if (invoice.discount_amount) {
                        // console.debug('Odoo discount');
                        const invoicePayment = new registerModels.InvoicePayment;

                        // Name is generated when the payment is created in odoo
                        invoicePayment.name = self.pos.generateNextPaymentNumber();
                        invoicePayment.date = tools.format_date(new Date());
                        invoicePayment.move_id = {id: invoice.id, name: invoice.name};
                        invoicePayment.pos_session_id = self.pos.pos_session.id;
                        invoicePayment.payment_method_id = self.pos.db.discount_payment_method.id;
                        invoicePayment.discount_amount = parseFloat(invoice.discount_amount);

                        invoicePaymentList.push(invoicePayment);
                    }
                });
            }

            return invoicePaymentList;
        },

        /**
         * @public
         */
        reload_pos_data: function () {
            this.payment_method_ids = this.pos.db.payment_method;
            this.journal_ids = this.pos.db.journal;
            this.partner_id = this.pos.get_client();
            this.selected_invoice = {};
            this.general_payments = {};
            this.discount_by_invoice = {};

            this.total_amount = 0;
            this.total_due = 0;
            this.invoice_ids = [];
            this.surcharge_amount = 0;
        },

        /**
         * @public
         */
        validate_payment: function () {
            const invoicePayments = this.build_invoice_payments();
            const self = this;

            if (invoicePayments && invoicePayments.length > 0) {
                const paymentGroup = new registerModels.PaymentGroup({
                    'name': self.pos.generateNextPaymentGroupNumber(),
                    'invoice_payment_ids': invoicePayments
                });

                console.log(paymentGroup.payment_amount_total);

                this.pos.gui.show_screen('invoicePaymentReceipt', {paymentGroup: paymentGroup});
                this.pos.synch_invoive_payment_and_surcharges(invoicePayments, []);
                _.each(self.invoice_ids, function (invoice) {
                    self._deselect_invoice();
                    invoice.amount_residual = invoice.expected_final_due;
                    invoice.discount_amount = 0;
                    _.each(self.pos.payment_methods, function (paymentMethod) {
                        self._update_invoice_payment_amount(invoice.id, paymentMethod.id, 0);
                    });
                });
            }
        },

        /**
         * @public
         */
        toggle_percentage_input: function () {
            this.$el.find("#discount_type-radio-percentage");
        },

        ////////////////////
        //     Events     //
        ////////////////////
        /**
         * @private
         */
        _toggle_surcharge_elements: function (event) {
            if (Object.hasOwnProperty.call(event, 'is_surcharge_paid')) {
                const isSurchargePaid = event['is_surcharge_paid'];
                this.$el.find(".js_hidden_when_surcharge").toggle(!!isSurchargePaid);
                this.$el.find(".js_hidden_when_no_surcharge").toggle(!isSurchargePaid);
            }
        },

        /**
         * @private
         */
        _update_discount_amount: function (event) {
            const invoice = event.invoice;
            invoice.discount_amount = event.amount;
            invoice.expected_final_due = invoice.amount_residual
                - tools.sum_object_properties(this._get_payment_method_amounts(invoice))
                - invoice.discount_amount;
            this.trigger("payment_amounts:update");
        },
    });

    gui.define_screen({name: 'pos_invoice_payment_register_widget', widget: PosInvoicePaymentRegisterWidget});

    return PosInvoicePaymentRegisterWidget;
});
