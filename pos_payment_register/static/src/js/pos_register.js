odoo.define('register_payments.pos_view', function(require) {
    "use strict";

    var screens = require("point_of_sale.screens")
    var PopupWidget = require('point_of_sale.popups');
    var gui = require("point_of_sale.gui")
    var core = require("web.core")
    var QWeb = core.qweb;

    // Payment
    var BtnRegisterPayment = screens.ActionButtonWidget.extend({
        template: "BtnRegisterPayment",

        button_click: function() {
            var self = this;
            this.gui.show_screen("invoice_list")
        },

        clear_button_fun: function() {
            var order = this.pos.get_order();
            order.remove_orderline(order.get_selected_orderline());
        }
    });

    screens.define_action_button({ 'name': 'clear_button_fun', 'widget': BtnRegisterPayment });

    // Invoices screeen
    var PosInvoiceScreenWidget = screens.ScreenWidget.extend({
        template: 'InvoicesLineWidget',
        back_screen: 'product',
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
        },

        clear: function(){
            
            // Remove invoice list
            var contents = this.$el[0].querySelector('.invoice-list-contents');
            var $contents = this.$(contents);
            $contents.empty();

            this._invoice_payments = {}
        },

        update: function(){
            var self = this;

            self.clear();

            // Logic
            self.partner_id = self.pos.get_client();
            self._get_unpaid_invoices(self.partner_id).then(function(invoice_ids){
                
                // Graphics
                self.print_header();
                self.print_invoices(invoice_ids);
            });
            
        },

        _get_unpaid_invoices: function(partner_id){
            var self = this;
            return self._rpc({
                model: "account.move",
                method: "search_read",
                args: [
                    [
                        ['state', '=', 'posted'],
                        ['invoice_payment_state', '!=', 'paid'],
                        ["type", "in", ["out_invoice"]],
                        ["partner_id", "=", partner_id.id],
                    ],
                    [
                        "name",
                        "journal_id",
                        "partner_id",
                        "invoice_date",
                        "invoice_date_due",
                        "amount_total",
                        "amount_residual",
                        "surcharge_invoice_id",
                        "is_overdue",
                    ]
                ],
                order: ["invoice_date_due", "name"]
            });
        },

        print_header: function(){
            var self = this;
            this.renderElement();
            this.$('.back').click(function() {
                self.gui.show_screen('products');
            });
        },


        print_invoices: function(invoice_ids) {
            var self = this;
            this.$('.back').click(function() {
                self.gui.show_screen('products');
            });
            console.log("queso: " + invoice_ids);

            this.render_invoice_list(invoice_ids);

            this.$('.invoice-list-contents').delegate('.invoice-line', 'click', function(event) {
                self.line_select(event, $(this), parseInt($(this).data('id')));
            });

            var search_timeout = null;

            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }

            var selected_invoice = this.gui.get_current_screen_param("selected-invoice");

            if (selected_invoice) {
                this.$(".invoice-list-contents .invoice-line").filter("[data-id=" + selected_invoice + "]").trigger("click");
            }
        },

        /**
         * @returns {Promise} A promise with all payment journals
         */
        get_payment_journal: function(){
            return this._rpc({
                model: "account.journal",
                method: "search_read",
                args: [
                    [
                        ["type", "in", ["bank", "cash"]],
                        ["inbound_payment_method_ids", "!=", false]
                    ],
                    [
                        "display_name",
                        "inbound_payment_method_ids",
                    ]
                ],
            });
        },

        /**
         * @returns {Promise} A promise with all payment methods
         */
        get_payment_methods: function(){
            return this._rpc({
                model: "account.payment.method",
                method: "search_read",
                args: [
                    [
                        ["payment_type", "=", "inbound"],
                    ],
                    ["name"]
                ],
            });
        },

        /**
         * Will be execute everytime this view is shown, here we update
         * and handle some logical things (Thanks odoo!!! ~Sarcasm~)
         */
        show: function() {
            this._super();
            var self = this;

            // Odoo only works with promises, so I just put the rpc calls in these methods
            var journals_promise = self.get_payment_journal();
            var payment_methods_promise = self.get_payment_methods();

            // This is used to wait until all the promises are resolved
            Promise.all([journals_promise, payment_methods_promise]).then(function(promises) {

                // This give us the promises, the order is the same as the arguments order
                var journal_ids = promises[0];
                var payment_method_ids = promises[1];

                // Settings
                self.new_payment_ids = {};
                self.set_session_journal_payment_group({});
                self.global_payments = {};

                // This is used for rendering and a better "payment editing interface"
                self.journal_ids = journal_ids;
                self.payment_method_ids = payment_method_ids;

                self.update();
            });
            // "['&amp;', ('invoice_date_due', '&lt;', time.strftime('%Y-%m-%d')), ('state', '=', 'posted'), ('invoice_payment_state', '=', 'not_paid')]"
        },

        math_sum: function(property, ...objs) {
            var suma = 0.0;
            objs.forEach(function(obj) {
                if (obj.hasOwnProperty(property)) {
                    var prop = obj[property];
                    if (!isNaN(prop)) {
                        suma += prop;
                    }
                }
            });
            return suma;
        },

        _redraw_money_values: function() {
            let journal_payment_group = this.get_session_journal_payment_group();
            let payment_total = 0;
            for (let journal_id in journal_payment_group) {
                if (journal_payment_group.hasOwnProperty(journal_id)) {
                    let journal_sum = this.math_sum("amount", ...journal_payment_group[journal_id]);
                    document.querySelector("#payment_ids .payment-row[data-journal-id='" + journal_id + "'] .payment-total").innerText = journal_sum.toFixed(2);
                    payment_total += journal_sum;
                }
            }
            this.$("#total_amount").text(parseFloat(payment_total).toFixed(2));
            this.$("#total_due").text(parseFloat(this.amount_due_total).toFixed(2));
            return true;
        },

        _update_total_payments: function() {
            var session_new_payments = this.get_session_new_payments()
            var journal_payment_group = this.set_session_journal_payment_group({});

            for (let payment in session_new_payments) {
                if (session_new_payments.hasOwnProperty(payment)) {
                    var payment_obj = session_new_payments[payment];
                    var payment_journal = payment_obj.payment_journal;
                    var keys = Object.keys(payment_journal);
                    keys.forEach(function(key) {
                        if (!journal_payment_group.hasOwnProperty(key)) {
                            journal_payment_group[key] = [];
                        }
                        journal_payment_group[key].push(payment_journal[key]);
                    });
                }
            }
            this._redraw_money_values();
            return journal_payment_group;
        },

        /**
         * Render an invoice list which is passed. It doesn't order the invoices.
         * @param {Array<Object>} invoice_ids A invoice array. The field name should be the same as the account.move model
         */
        render_invoice_list: function(invoice_ids) {
            var self = this;

            // Remove old invoice list
            var contents = this.$el[0].querySelector('.invoice-list-contents');
            var $contents = this.$(contents);
            $contents.empty();
            
            contents.innerHTML = "";
            if (!this.pos.has("session_payments")) {
                this.pos.set("session_payments", {});
            }

            var session_payments = this.pos.get("session_payments");

            var amount_total = 0.0;
            var amount_residual = 0.0;
            var session_payment_total = 0.0;

            if (!this.pos.has("session_new_payments")) {
                this.pos.set("session_new_payments", {});
            }

            var session_new_payments = this.pos.get("session_new_payments");

            for (var invoice_id of invoice_ids){

                if (!session_new_payments.hasOwnProperty(invoice_id.id)) {
                    session_new_payments[invoice_id.id] = {
                        "id": invoice_id.id,
                        "name": invoice_id.name,
                        "partner_id": invoice_id.partner_id,
                        "payment_journal": {},
                        "invoice_date": new Date(invoice_id.invoice_date),
                        "invoice_date_due": new Date(invoice_id.invoice_date_due),
                        "amount_total": invoice_id.amount_total,
                        "amount_due": invoice_id.amount_residual,
                    };

                    this.journal_ids.forEach(function(journal) {
                        session_new_payments[invoice_id.id].payment_journal[journal.id] = {
                            "amount": 0.0,
                            "payment_method_id": journal.inbound_payment_method_ids[0],
                        };
                    });
                }

                if (session_payments.hasOwnProperty(invoice_id.id.toString())) {
                    invoice_id.session_payment = session_payments[invoice_id.id.toString()];
                } else {
                    invoice_id.session_payment = session_payments[invoice_id.id.toString()] = 0.0;
                }

                amount_total += invoice_id.amount_total;
                amount_residual += invoice_id.amount_residual;
                session_payment_total += invoice_id.session_payment;

                // Because we receive as text, we need to convert it to html to append it
                var invoice_raw_html_row = QWeb.render('PosInvoiceLine', { widget: this, invoice_id: invoice_id });
                var aux_tbody = document.createElement('tbody');
                
                // Text to HTMLElement convertion
                aux_tbody.innerHTML = invoice_raw_html_row;
                var invoice_html_row = aux_tbody.childNodes[1];
                
                // Check colors
                if(invoice_id.is_overdue){
                    $(invoice_html_row).addClass("overdue");
                }
                contents.appendChild(invoice_html_row);
            }

            var invoice_line = document.createElement('tbody');
            invoice_line.innerHTML = "<tr> " +
                "<td></td>" +
                "<td></td>" +
                "<td></td>" +
                "<td></td>" +
                "<td></td>" +
                "<td>" + amount_total + "</td>" +
                "<td>" + amount_residual + "</td>" +
                "<td>" + session_payment_total + "</td>" +
                "</tr>";
            this.amount_due_total = amount_residual;
            invoice_line = invoice_line.childNodes[0];
            contents.appendChild(invoice_line);
            this.display_invoice_details('hide', invoice_id)
        },
        
        line_select: function(event, $line, id) {
            var self = this;

            var fnc_select_element = function(values) {
                self.$('.invoice-list .lowlight').removeClass('lowlight')

                var invoice = values[0];
                var payments = values[1];
                invoice.payments = payments;

                if ($line.hasClass('highlight')) {
                    $line.removeClass('highlight');
                    $line.addClass('lowlight');
                    self.display_invoice_details('hide', invoice)
                } else {
                    self.$('.invoice-list .highlight').removeClass('highlight')
                    $line.addClass('highlight');
                    var y = event.pageY - $line.parent().offset().top;
                    self.invoice = invoice;
                    self.display_invoice_details('show', invoice, y);
                }
            }

            var payments = this._rpc({
                model: "account.payment",
                method: "search_read",
                args: [
                    [
                        ["invoice_ids", "=", id],
                        ["state", "=", "posted"]
                    ],
                    [
                        "name",
                        "amount",
                        "journal_id",
                    ]
                ],
            });

            var invoice = this._rpc({
                model: "account.move",
                method: "search_read",
                args: [
                    [
                        ["id", "=", id]
                    ],
                    [
                        "name",
                        "amount_total",
                        "amount_residual",
                        "partner_id",
                        "invoice_date",
                        "journal_id",
                        // "_get_reconciled_info_JSON_values",
                    ]
                ],
            })


            Promise.all([invoice, payments]).then(fnc_select_element);


            //.then(fnc_select_element);
            /*             var order = this.get_order_by_id(id);
                        $line.addClass('highlight');
                        this.gui.show_popup('order', {
                            'order': order,
                            'line': $line
                        }) */
        },

        new_payment_parameter_changed: function(input, parameter, value) {
            if (!this.pos.has("session_new_payments")) {
                this.pos.set("session_new_payments", {});
            }

            var session_new_payments = this.pos.get("session_new_payments");
            var invoice = this.invoice[0];

            var $input = $(input);
            var payment_journal_id = $input.parent(".payment-row").data("journal-id");
            if (!session_new_payments.hasOwnProperty(invoice.id)) {
                session_new_payments[invoice.id] = {
                    "id": invoice.id,
                    "name": invoice.name,
                    "partner_id": invoice.partner_id,
                };
            }
            if (!session_new_payments[invoice.id].hasOwnProperty("payment_journal")) {
                session_new_payments[invoice.id].payment_journal = {};
            }
            if (!session_new_payments[invoice.id].payment_journal.hasOwnProperty(payment_journal_id)) {
                session_new_payments[invoice.id].payment_journal[payment_journal_id] = { "amount": 0.0 };
            }
            session_new_payments[invoice.id].payment_journal[payment_journal_id][parameter] = value;
        },
        _set_from_pos: function(parameter, value) {
            this.pos.set(parameter, value);
            var var_pos = this.pos.get(parameter);
            return var_pos;
        },

        _get_from_pos: function(parameter, default_value) {
            if (!this.pos.has(parameter)) {
                this.pos.set(parameter, default_value);
            }

            var session_new_payments = this.pos.get(parameter);
            return session_new_payments;
        },
        set_session_journal_payment_group: function(value) {
            return this._set_from_pos("journal_payment_group", value);
        },

        get_session_journal_payment_group: function() {
            return this._get_from_pos("journal_payment_group", {});
        },
        get_session_new_payments: function() {
            return this._get_from_pos("session_new_payments", {});
        },
        get_total_payment: function() {
            return this._get_from_pos("total_payment", { "1": 240 });
        },
        get_total_invoice: function() {
            return this._get_from_pos("total_invoice", {
                "name": "Total"
            });
        },

        display_invoice_details: function(visibilty, invoice, clickpos) {
            if (invoice) {
                var self = this;

                var contents = this.$('.invoice-details-contents');
                var parent = this.$('invoice-list').parent();
                var scroll = parent.scrollTop();
                var height = contents.height();
                var $button_validate = this.$(".button.next");
                var $button_register = this.$(".button.register_payment");

                var payments = invoice.payments;

                var session_new_payments = this.get_session_new_payments();
                var total_invoice = this.get_total_invoice()

                var payment_methods_dict = {}
                this.payment_method_ids.forEach(function(method_id) {
                    payment_methods_dict[method_id.id] = method_id;
                })

                if (visibilty === "show") {
                    invoice = invoice[0];
                } else if (visibilty === "hide") {
                    invoice = total_invoice;
                }

                //We invoke it this way because we need that
                //"this"'s value is "self", not the button...
                //Sorry my bad english :P
                $button_validate.off("click");
                $button_validate.on("click", function() { self.invoice_validate_payment() });

                $button_register.off("click");
                $button_register.on("click", function() { self.invoice_register_payment() });

                var $payment_dashboard = $(QWeb.render('InvoiceDetails', {
                    "move": total_invoice,
                    "journal_ids": this.journal_ids,
                    "payment_method_dict": payment_methods_dict,
                }))


                $($payment_dashboard).find("input[name^='journal_payment_amount']").on("keyup", function() {
                    self.new_payment_parameter_changed(this, "amount", parseFloat(this.value))
                    self._update_total_payments();
                });
                //
                $($payment_dashboard).find("input[name^='payment_method_id']").on("change", function() {
                    self.new_payment_parameter_changed(this, "payment_method_id", parseInt(this.value))
                    self._update_total_payments();
                });

                // Fill with current session values if exists
                if (session_new_payments.hasOwnProperty(invoice.id) &&
                    session_new_payments[invoice.id].hasOwnProperty("payment_journal") &&
                    session_new_payments[invoice.id].payment_journal
                ) {
                    var payment_journals = session_new_payments[invoice.id].payment_journal;
                    for (var journal in payment_journals) {
                        var journal_vals = payment_journals[journal];
                        if (journal_vals.hasOwnProperty("amount")) {
                            $payment_dashboard.find("#journal_payment_amount-" + journal).val(journal_vals.amount)
                        }
                        if (journal_vals.hasOwnProperty("payment_method_id")) {
                            $payment_dashboard.find("input[name^='payment_method_id-" + journal + "']").prop("checked", false);
                            // let
                            let $payment_method_el = $payment_dashboard.find("#payment_method-" + journal + "-" + journal_vals.payment_method_id);
                            let payment_method_el = $payment_method_el[0];
                            if ($payment_method_el) {
                                payment_method_el.checked = true;
                                // $payment_method_el.prop("checked", true);
                                this.new_payment_parameter_changed(payment_method_el, "payment_method_id", parseInt($payment_method_el.val()));
                            }
                        }
                    }
                }

                contents.empty();
                contents.append($payment_dashboard);

                if (visibilty === "show") {
                    contents.find("#payment_ids .payment-row").each(function(index, element) {
                        var $payment_type_amount = element.querySelector(".payment-text");
                        var journal_payments = payments.filter(function(payment) { return payment.journal_id[0] == $(element).data("journal-id") })

                        var total = 0.0;
                        for (var i = 0; i < journal_payments.length; i++) {
                            total += journal_payments[i].amount;
                        }

                        $($payment_type_amount).text(total.toFixed(2));
                    })
                } else {
                    this.select_mode = "global";
                    $payment_dashboard.find("input[name^='journal_payment_amount']").off("keyup");
                    $payment_dashboard.find("input[name^='payment_method_id']").off("change");

                    $payment_dashboard.find("input[name^='journal_payment_amount']").on("keyup", function() {
                        let journal_id = parseInt(this.dataset["journalId"]);
                        self._set_global_amount(journal_id, parseFloat(this.value));
                        self._update_total_payments();
                    });
                    console.log("payments!!!")
                }

                var new_height = contents.height();
                this._update_total_payments();

                if (!this.details_visible) {
                    parent.height("-=" + new_height);

                    if (clickpos < scroll + new_height + 20) {
                        parent.scrollTop(clickpos - 20);
                    } else {
                        parent.scrollTop(parent.scrollTop() + new_height);
                    }
                } else {
                    parent.scrollTop(parent.scrollTop() - height + new_height);
                }

                this.details_visible = true;
            }
        },

        _set_global_amount: function(journal, new_amount) {
            if (!this.global_payments.hasOwnProperty(journal)) {
                this.global_payments[journal] = {
                    "amount": 0.0,
                    "payment_method_id": false,
                };
            }
            this.global_payments[journal].amount = new_amount;
        },

        invoice_register_payment: function() {
            var self = this;

            var session_new_payments = this.get_session_new_payments();

            var invoice_values = Object.values(session_new_payments).sort(function(a, b) {
                return a.invoice_date - b.invoice_date;
            });

            let i = 0;
            for (const journal_id in this.global_payments) {
                if (this.global_payments.hasOwnProperty(journal_id)) {
                    const journal = this.global_payments[journal_id];
                    while (i < invoice_values.length && (journal.amount > 0)) {
                        let invoice = invoice_values[i];
                        if (invoice.amount_due > 0) {
                            if (journal.amount - invoice.amount_due >= 0) {

                                // invoice.payment_journal[journal_id].amount += invoice.amount_due;
                                session_new_payments[invoice.id].payment_journal[journal_id].amount += invoice.amount_due;

                                // invoice.amount_due = 0;
                                session_new_payments[invoice.id].amount_due = 0;

                                journal.amount -= invoice.amount_due;
                                i++;
                            } else {
                                // invoice.payment_journal[journal_id].amount += journal.amount;
                                session_new_payments[invoice.id].payment_journal[journal_id].amount += journal.amount;

                                // invoice.amount_due -= journal.amount;
                                session_new_payments[invoice.id].amount_due -= journal.amount;
                                journal.amount = 0;
                                break;
                            }
                        } else {
                            i++;
                        }
                    }
                    console.log(journal.amount);
                }
            }

            this._update_total_payments();

            console.log("global_amount: " + this.global_payments);
        },

        invoice_validate_payment: function() {
            var self = this;
            if (this.pos.has("session_new_payments")) {
                var today = new Date();

                var year = today.getFullYear();
                var month = ("0" + today.getMonth()).slice(-2);
                var day = ("0" + today.getDate()).slice(-2);

                var str_today = year + "-" + month + "-" + day;
                var session_new_payments = this.pos.get("session_new_payments");
                var payment_multiple_dict = [];

                for (var invoice_id in session_new_payments) {
                    var invoice = session_new_payments[invoice_id];
                    if (invoice.hasOwnProperty("payment_journal")) {
                        for (var journal in invoice.payment_journal) {
                            if (invoice.payment_journal[journal].amount &&
                                invoice.payment_journal[journal].amount > 0) {
                                var payment_dict = {
                                    "payment_type": "inbound",
                                    "journal_id": parseInt(journal),
                                    "partner_type": "customer",
                                    "amount": parseFloat(invoice.payment_journal[journal].amount),
                                    "payment_method_id": invoice.payment_journal[journal].payment_method_id,
                                    "payment_date": str_today,
                                    "partner_id": parseInt(invoice.partner_id[0]),
                                    "invoice_ids": [
                                        [4, invoice.id, 0]
                                    ],
                                    "communication": invoice.name
                                }
                                payment_multiple_dict.push(payment_dict);
                            }
                        }
                    }
                }
                console.log(payment_multiple_dict);

                this._rpc({
                    model: "account.payment",
                    method: "create",
                    args: [payment_multiple_dict],
                }).then(function(invoice_ids) {
                    self._rpc({
                        model: "pos_payment_register.payment_group",
                        method: "create",
                        args: [
                            {}
                        ],
                    }).then(function(payment_group_id) {
                        var put_payment_in_group = self._rpc({
                            model: "account.payment",
                            method: "write",
                            args: [
                                invoice_ids,
                                { "payment_group_id": payment_group_id[0] }
                            ],
                        })
                        var post_payment = self._rpc({
                            model: "account.payment",
                            method: "post",
                            args: [
                                invoice_ids,
                            ],
                        })
                        Promise.all([put_payment_in_group, post_payment]).then(function(promises) {
                            alert(promises);
                            session_new_payments
                            self.show(); //gui.show_screen("invoice_list", true);
                        });
                    })
                });
            } else {
                console.error("No payment to write")
            }
        },
    });

    gui.define_screen({ name: 'invoice_list', widget: PosInvoiceScreenWidget });
});