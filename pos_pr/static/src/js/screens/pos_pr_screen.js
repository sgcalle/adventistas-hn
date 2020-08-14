odoo.define('pos_pr.screen.invoice_payment', function (require) {

    const screens = require("point_of_sale.screens");

    const gui = require("point_of_sale.gui");
    const core = require("web.core");
    const resgister_models = require("pos_pr.models");

    const tools = require('pos_pr.tools')

    const AccountMove = resgister_models.AccountMove;

    const QWeb = core.qweb;

    const _t = core._t;
    const exports = {};

    // Invoices screeen
    let PosInvoicePaymentRegisterWidget = screens.ScreenWidget.extend({

        events: {
            'click .back': '_go_to_back_screen',
            'click .invoice-list__content-line': '_toggle_invoice_selection',
            'payment_amounts:update .screen-content': '_redraw_amounts',
            'click .apply-payments': '_apply_general_payment_to_invoices',
            'click .validate-payments': 'validate_payment',
            'click .pay-surcharge': 'pay_surcharge',
            'click .cancel-surcharge': 'cancel_surcharge',
        },

        back_screen: 'products',
        template: 'InvoicesLineWidget',

        init: function (options) {
            this._super(options);
            this.pos.register_payment = this;
            this.global_invoice_payments_by_partner_id = {};
            // this.global_surcharge_invoice_by_partner_id = {};
            this.free_of_surcharge = {};
        },

        render_message: function (message) {
            let $content = this.$el.find(".register-content");
            let messageContent = document.createElement("div");
            messageContent.innerHTML = "<h1>" + message + "</h1>";
            messageContent.classList.add("background-message");
            $content.append(messageContent);
        },

        show: function (refresh) {
            this._super(); // We need to check if the user has selected a customer
            let self = this;

            if (!refresh) {
                this._reload_pos_data();
            }
            this._clear_register_dashboard();
            if (this.pos.get_cashier().role !== 'manager') {
                this.$el.find('.js-global-free-surcharge').addClass("oe_hidden")
            } else {
                this._show_free_surcharge_input();
            }
            if (this.partner_id) {
                this._render_invoices();
                this._redraw_amounts();

                let js_global_total_surcharge_input = this.el.querySelector(".js-global-total-surcharge-input");
                NumberInput(js_global_total_surcharge_input, {decimal_limit: 2});

                let js_global_free_surcharge_input = this.el.querySelector(".js-global-free-surcharge-input");
                js_global_free_surcharge_input.value = (this.free_of_surcharge[this.partner_id.id] || 0) || 0;

                NumberInput(js_global_free_surcharge_input, {decimal_limit: 2});

                js_global_free_surcharge_input.addEventListener("input", event => {
                    self.free_of_surcharge[self.partner_id.id] = parseFloat(js_global_free_surcharge_input.value);
                });

                this._toggle_surcharge_elements();

            } else {
                this.render_message(_t("No customer has been selected"));
            }
        },

        _show_free_surcharge_input: function () {
            let self = this;
            let $global_free_surcharge_tr = this.$el.find('.js-global-free-surcharge');
            $global_free_surcharge_tr.removeClass("oe_hidden");
            let $global_free_surcharge_input = $global_free_surcharge_tr.find(".js-global-free-surcharge-input");
            $global_free_surcharge_input.on("input", function () {
                let free_of_surcharge = parseFloat($global_free_surcharge_input.val());
                let surcharge_computed = isNaN(self.surcharge_amount - free_of_surcharge) ? self.surcharge_amount : self.surcharge_amount - free_of_surcharge;
                self.$el.find(".js-global-total-surcharge input").val(surcharge_computed.toFixed(2));
            });
        },


        _reload_pos_data: function () {
            this.payment_method_ids = this.pos.db.payment_method;
            this.journal_ids = this.pos.db.journal;
            this.partner_id = this.pos.get_client();
            this.selected_invoice = {};
            this.general_payments = {};
            this.total_amount = 0;
            this.total_due = 0;
            this.invoice_ids = [];
            this.surcharge_amount = 0;
        },

        _clear_register_dashboard: function () {
            this.$el.find("table.invoice-list tbody.invoice-list__content").empty();
            this._draw_payment_dashboard()

            // this.$el.find(".invoice-details-contents").empty();
            this.$el.find(".background-message").remove();
        },

        _render_invoices: function () {
            let invoice_ids = this.pos.db.due_invoices.filter(invoice =>
                invoice.partner_id[0] === this.partner_id.id && invoice.amount_residual > 0
            );
            this.invoice_ids = invoice_ids;
            if (invoice_ids.length) {
                this._print_invoice_list(invoice_ids);
            } else {
                this.render_message(_.str.sprintf(
                    _t("%s has no due invoice"),
                    this.partner_id.name)
                );
            }
        },

        _print_invoice_list: function (invoice_ids) {
            let self = this;
            let total_surcharge = 0;
            _.each(invoice_ids, function (invoice_id) {
                let invoice_row = QWeb.render('PosInvoiceLine', {
                    "invoice_id": invoice_id,
                });


                let $invoice_row = $(invoice_row.trim());

                let invoice_due_date = new Date(invoice_id.invoice_date_due || invoice_id.invoice_date);
                let today_date = new Date();
                today_date.setHours(0, 0, 0, 0)

                if (invoice_due_date < today_date) {
                    $invoice_row.addClass("overdue");
                    total_surcharge += invoice_id.surcharge_amount;
                } else if (invoice_due_date.getTime() === today_date.getTime()) {
                    $invoice_row.addClass("overdue-today");
                    total_surcharge += invoice_id.surcharge_amount;
                }

                self.$el.find("table.invoice-list tbody.invoice-list__content").append($invoice_row);
            });

            this.surcharge_amount = parseFloat(total_surcharge);
            self.$el.find(".js-global-total-surcharge input").val(total_surcharge - (this.free_of_surcharge[this.partner_id.id] || 0));
            this._toggle_surcharge_elements();
        },

        _toggle_surcharge_elements: function () {
            let is_surcharge_paid = this.surcharge_amount - (this.free_of_surcharge[this.partner_id.id] || 0) === 0;
            this.$el.find(".js_hidden_when_surcharge").toggle(!!is_surcharge_paid);
            this.$el.find(".js_hidden_when_no_surcharge").toggle(!is_surcharge_paid);
        },

        _go_to_back_screen: function () {
            this.gui.show_screen(this.back_screen);
        },

        _toggle_invoice_selection: function (event) {

            if (this.surcharge_amount - (this.free_of_surcharge[this.partner_id.id] || 0) === 0) {
                let invoice_row = event.currentTarget;

                this._toggle_select_class(invoice_row);
                this._redraw_amounts();

                let invoice = this._get_invoice_by_html(invoice_row);

                if (this.selected_invoice.id === invoice.id) {
                    this._deselect_invoice(invoice);
                } else {
                    this._select_invoice(invoice);
                }
            }
        },

        _toggle_select_class: function (invoice) {
            let is_current_row_selected = $(invoice).hasClass("invoice-list__content-line--selected");
            this.$el.find(".invoice-list__content-line").removeClass("invoice-list__content-line--selected")
            if (!is_current_row_selected) {
                $(invoice).toggleClass("invoice-list__content-line--selected")
            }
        },

        _get_invoice_by_html: function (invoice_html_row) {
            let invoice_id = parseInt(invoice_html_row.dataset["id"]);
            return this.pos.db.due_invoices_by_id[invoice_id];
        },

        _deselect_invoice: function (invoice) {
            this.selected_invoice = {};
            this.$el.find(".apply-payments").show();
            this._draw_payment_dashboard();
            console.log("Deselect invoice: " + invoice.name)
        },
        _select_invoice: function (invoice) {
            this.selected_invoice = invoice;
            this._draw_selected_invoice_payments();
            console.log("Select invoice: " + invoice.name);
        },

        _draw_selected_invoice_payments: function () {
            this.$el.find(".apply-payments").hide();
            this._draw_payment_dashboard(this.selected_invoice);
        },

        _draw_payment_dashboard: function (invoice) {
            let $content = this.$el.find(".invoice-details-contents");
            $content.empty();

            if (invoice) {
                let invoice_details = this._get_invoice_details_qweb(invoice);
                $content.append(invoice_details);
            }

            let get_payment_method_qweb = this._get_payment_method_qweb(invoice);
            $content.append(get_payment_method_qweb);

            this._toggle_surcharge_elements();
            this._add_event_listeners_to_payment_form();
        },

        _get_invoice_details_qweb: function (invoice) {
            let invoice_details = QWeb.render('InvoiceDetails', {
                "widget": this,
                "move": invoice,
                "journal_by_id": this.pos.db.journal_by_id,
            });
            return $(invoice_details.trim());
        },

        _get_payment_method_qweb: function (invoice) {
            let payment_methods_amounts = this._get_payment_method_amounts(invoice);
            let payment_method_qweb = QWeb.render('PaymentList', {
                "widget": this,
                "move": invoice,
                "payment_method_ids": this.pos.payment_methods,
                "payment_methods_amounts": payment_methods_amounts
            });
            return $(payment_method_qweb.trim());
        },

        _get_payment_method_amounts: function (invoice) {
            let lookup_invoice_payments = this.general_payments;


            if (invoice) {
                let invoice_id = typeof invoice === 'object' ? invoice.id : invoice;
                let global_invoice_payments = this._get_value_with_default(this.global_invoice_payments_by_partner_id, this.partner_id.id, {});
                lookup_invoice_payments = this._get_value_with_default(global_invoice_payments, invoice_id, {})
            }

            let payment_amounts = {};
            _.each(this.pos.payment_methods, (payment_method) => {
                payment_amounts[payment_method.id] = this._get_value_with_default(lookup_invoice_payments, payment_method.id, 0.0);
            })
            return payment_amounts;
        },

        _add_event_listeners_to_payment_form: function () {
            let self = this;
            this.$el.find(".input-payment-method").each(function (index, payment_method_row) {
                let $payment_method_row = $(payment_method_row);

                let invoice_id = self.selected_invoice.id;
                let payment_method_id = parseInt($payment_method_row.data("id"));

                $payment_method_row.find("input").on("keydown keyup change", (event) => {
                    let payment_method_input = event.currentTarget;
                    let amount = payment_method_input.value;

                    self._update_invoice_payment_amount(invoice_id, payment_method_id, amount);
                }).each((index, element) => {
                    NumberInput(element, {decimal_limit: 2});
                });

                $payment_method_row.find("input").on("cut copy paste", function (e) {
                    e.preventDefault();
                });
            });
        },

        _update_invoice_payment_amount(invoice_id, payment_method_id, amount) {
            if (amount === 0) {
                console.log("HELP!!!!", invoice_id, payment_method_id, amount)
            }
            let global_invoice_payments = this._get_value_with_default(this.global_invoice_payments_by_partner_id, this.partner_id.id, {});
            let invoice_payment_methods = this._get_value_with_default(global_invoice_payments, invoice_id, {});

            let looking_payment_amount_object = invoice_id ? invoice_payment_methods : this.general_payments;

            looking_payment_amount_object[payment_method_id] = tools.cast_to_float(amount);

            if (invoice_id) {
                let invoice = this.pos.db.due_invoices_by_id[invoice_id];
                invoice.expected_final_due = invoice.amount_residual - tools.sum_object_properties(this._get_payment_method_amounts(invoice))
                console.log(invoice.name, invoice.expected_final_due);
            }
            this.$el.find(".screen-content").trigger("payment_amounts:update");
            console.log(this.global_invoice_payments_by_partner_id, invoice_id, payment_method_id, amount)
        },

        _get_value_with_default: function (object, key, default_value) {
            if (!Object.prototype.hasOwnProperty.call(object, key)) {
                object[key] = default_value;
            }
            return object[key];
        },

        _redraw_amounts: function () {
            this._render_global_payment_amounts();
            this._refresh_invoice_lines_values();
        },

        _refresh_invoice_lines_values: function () {
            let self = this;
            if (this.invoice_ids) {
                _.each(this.invoice_ids, (invoice) => {
                    let $invoice_row = self.$el.find(_.str.sprintf('.invoice-list__content-line[data-id=%s]', invoice.id));
                    $invoice_row.find(".js-expected-final-due").text(invoice.expected_final_due.toFixed(2));
                });
            }
        },

        _render_global_payment_amounts: function () {

            let total = 0;
            let total_due = tools.sum_object_properties(this.invoice_ids.map((invoice) => invoice.amount_residual));

            let global_invoice_payments = this.global_invoice_payments_by_partner_id[this.partner_id.id];
            if (global_invoice_payments) {
                total = tools.sum_object_properties(Object.values(global_invoice_payments).map(tools.sum_object_properties));
            }

            this.total_amount = total;
            this.total_due = total_due;

            this.$el.find('.js-global-total-paid').text(total.toFixed(2));

            let global_total_due = (total_due - total).toFixed(2);

            this.$el.find('.js-global-total-due').text(global_total_due);
            this._toggle_surcharge_elements();
        },

        _apply_general_payment_to_invoices: function () {
            if (this.invoice_ids) {
                let global_invoice_payments = this._get_value_with_default(this.global_invoice_payments_by_partner_id, this.partner_id.id, {});
                let due_invoices = _.filter(this.invoice_ids, (invoice) => invoice.expected_final_due > 0);
                _.each(due_invoices, (invoice_id) => {
                    this._apply_general_payment_to_invoice(global_invoice_payments, invoice_id);
                });
                this.show(true);
            }
        },

        _apply_general_payment_to_invoice: function (global_invoice_payments, invoice_id) {
            let invoice_payment_methods = this._get_value_with_default(global_invoice_payments, invoice_id.id, {});
            let total_paid_to_invoice = 0;
            _.each(this.pos.payment_methods, (payment_method_id) => {
                total_paid_to_invoice += this._try_to_apply_payment_to_invoice(payment_method_id, invoice_id, invoice_payment_methods);
            });
            console.log("Applied total: ", invoice_id.name, total_paid_to_invoice);
            invoice_id.expected_final_due = invoice_id.amount_residual - total_paid_to_invoice;
        },

        _try_to_apply_payment_to_invoice: function (payment_method_id, invoice_id, invoice_payment_methods) {
            let general_pay = this.general_payments[payment_method_id.id];
            let amount_to_pay = Math.min(invoice_id.expected_final_due, general_pay);

            if (amount_to_pay > 0) {
                this.general_payments[payment_method_id.id] -= amount_to_pay;
                this._update_invoice_payment_amount(invoice_id.id, payment_method_id.id, (invoice_payment_methods[payment_method_id.id] || 0) + amount_to_pay);
                console.log("Applied: ", amount_to_pay, payment_method_id.name, invoice_id.name);
            }
            return amount_to_pay;
        },

        _extract_invoice_payments: function () {
            let invoice_payment_list = [];
            if (this.invoice_ids) {
                let self = this;
                _.each(this.invoice_ids, (invoice) => {
                    let invoice_payment_amounts = this._get_payment_method_amounts(invoice);
                    _.each(this.pos.payment_methods, (payment_method) => {

                        let invoice_payment = new resgister_models.InvoicePayment;

                        let invoice_payment_amount = invoice_payment_amounts[payment_method.id];
                        if (invoice_payment_amount > 0) {

                            // invoice_payment.name = 'a';
                            // Name is generated when the payment is created in odoo
                            invoice_payment.date = tools.format_date(new Date());
                            invoice_payment.payment_amount = invoice_payment_amounts[payment_method.id];
                            invoice_payment.payment_method_id = payment_method.id;
                            invoice_payment.move_id = invoice.id;
                            invoice_payment.pos_session_id = self.pos.pos_session.id;

                            invoice_payment_list.push(invoice_payment);

                        }
                    });
                });
            }

            return invoice_payment_list;
        },

        _generate_surcharge: function () {
            // let surcharge_pay_amount = this._get_surcharge_pay_amount()
            // let surcharge_payment_invoice_ids = this._clear_all_invoices_surcharge(surcharge_pay_amount);

            let surcharge_id = new resgister_models.SurchargeInvoice;
            surcharge_id.date = tools.format_date(new Date());
            surcharge_id.pos_session_id = this.pos.pos_session.id;
            surcharge_id.partner_id = this.partner_id.id;
            surcharge_id.free_of_surcharge = (this.free_of_surcharge[this.partner_id.id] || 0) || 0;

            let surcharge_payment_invoice_ids = this._clear_all_invoices_surcharge(surcharge_id);
            this._append_payments_to_surcharge(surcharge_id, surcharge_payment_invoice_ids);

            surcharge_id.amount = tools.sum_object_properties(surcharge_id.payment_ids.map(payment_id => payment_id.payment_amount));

            return surcharge_id;
        },

        _get_surcharge_pay_amount: function () {
            let surcharge_total = this._get_surcharge_total()
            let payment_total = this._get_payment_total()

            return Math.min(surcharge_total, payment_total)
        },

        _get_surcharge_total: function () {
            return parseFloat(this.el.querySelector(".js-global-total-surcharge-input").value);
        },

        _get_payment_total: function () {

            let amount_total = 0;

            _.each(this.pos.payment_methods, payment_method_id => {
                let $payment_tr = this.$el.find(".payment-method-list .input-payment-method[data-id='" + payment_method_id.id + "']");
                let input_val = parseFloat($payment_tr.find("input").val());
                amount_total += input_val || 0;
            });

            return parseFloat(amount_total);
        },

        _clear_all_invoices_surcharge: function (surcharge_id) {
            let surcharge_payment_invoice_ids = {}

            let invoice_payments_amounts = Object.values(this._get_current_dashboard_payments()) || [];
            invoice_payments_amounts = Array.prototype.filter.call(invoice_payments_amounts, payment_id => payment_id.payment_amount > 0);
            let payment_method_index = 0;

            let invoice_ids_with_surcharge = this.invoice_ids.filter(invoice_id => invoice_id.surcharge_amount > 0);
            this.free_of_surcharge[this.partner_id.id] = this.free_of_surcharge[this.partner_id.id] || 0;
            if (invoice_payments_amounts.length > 0) {
                for (let invoice_id of invoice_ids_with_surcharge) {

                    if (invoice_id.surcharge_amount <= 0 && payment_method_index >= invoice_payments_amounts.length) {
                        break;
                    } else {
                        if (surcharge_id.move_ids.indexOf(invoice_id.id) === -1) {
                            surcharge_id.move_ids.push(invoice_id.id);
                        }
                    }

                    if ( this.free_of_surcharge[this.partner_id.id] > 0) {
                        let free_of_surcharge_amount = Math.min(invoice_id.surcharge_amount, (this.free_of_surcharge[this.partner_id.id] || 0));
                        invoice_id.surcharge_amount -= free_of_surcharge_amount;
                        this.free_of_surcharge[this.partner_id.id] -= free_of_surcharge_amount;
                        this.surcharge_amount -= free_of_surcharge_amount;
                    }

                    while (invoice_id.surcharge_amount > 0 && payment_method_index < invoice_payments_amounts.length) {

                        let payment_id = invoice_payments_amounts[payment_method_index]
                        let sucharge_total_payment = surcharge_payment_invoice_ids[payment_id.payment_method_id] || 0;

                        let invoice_to_pay = Math.min(invoice_id.surcharge_amount, payment_id.payment_amount);
                        payment_id.payment_amount -= invoice_to_pay;

                        invoice_id.surcharge_amount -= invoice_to_pay
                        this.surcharge_amount -= invoice_to_pay;
                        sucharge_total_payment += invoice_to_pay;

                        if (payment_id.payment_amount <= 0) {
                            payment_method_index++;
                        }

                        this._update_invoice_payment_amount(undefined, payment_id.payment_method_id, payment_id.payment_amount);
                        surcharge_payment_invoice_ids[payment_id.payment_method_id] = sucharge_total_payment;
                    }

                }
            }

            this.show(true);

            return surcharge_payment_invoice_ids;
        },

        _get_current_dashboard_payments: function () {
            let self = this;
            let payments = {};

            this.$el.find(".payment-method-list tr.input-payment-method").each((index, el) => {

                let payment_amount = parseFloat(el.querySelector("input").value) || 0;
                let invoice_payment = new resgister_models.InvoicePayment;

                invoice_payment.date = tools.format_date(new Date());
                invoice_payment.payment_amount = payment_amount;
                invoice_payment.payment_method_id = parseInt(el.dataset.id);
                invoice_payment.pos_session_id = self.pos.pos_session.id;

                payments[invoice_payment.payment_method_id] = invoice_payment;

            });

            return payments;
        },

        _append_payments_to_surcharge: function (surcharge_id, surcharge_payment_invoice_ids) {
            let self = this;

            for (let payment_method_id in surcharge_payment_invoice_ids) {
                if (Object.prototype.hasOwnProperty.call(surcharge_payment_invoice_ids, payment_method_id)) {

                    let payment_amount = parseFloat(surcharge_payment_invoice_ids[payment_method_id]);
                    let invoice_payment = new resgister_models.InvoicePayment;

                    invoice_payment.date = tools.format_date(new Date());
                    invoice_payment.payment_amount = payment_amount;
                    invoice_payment.payment_method_id = parseInt(payment_method_id);
                    invoice_payment.pos_session_id = self.pos.pos_session.id;

                    surcharge_id.payment_ids.push(invoice_payment);

                }
            }

        },

        validate_payment: function () {
            // let surcharge = this._generate_surcharge();
            let invoice_payments = this._extract_invoice_payments();
            this.pos.send_invoice_payments(invoice_payments);
        },

        pay_surcharge: function () {
            let surcharge_id = this._generate_surcharge();
            this.pos.send_surcharge(surcharge_id);
            this.show(true);
            // this._toggle_surcharge_elements();

            // _.each(this.invoice_ids, invoice_id => {
            //      invoice_id.original_surcharge = invoice_id.surcharge_amount;
            // });


        },

    });

    gui.define_screen({name: 'pos_invoice_payment_register_widget', widget: PosInvoicePaymentRegisterWidget});

    return PosInvoicePaymentRegisterWidget;
});
