odoo.define("pos_pr.payment_register.components.invoice_list.screen", function (require) {

    const PosBaseWidget = require('point_of_sale.BaseWidget');
    const core = require("web.core");
    const _t = core._t;

    const InvoiceListRow = PosBaseWidget.extend({
        template: 'PaymentRegister.components.invoiceList.row',

        /**
         * @override
         */
        init: function (parent, invoice) {
            this._super(parent);
            this.invoice_id = invoice;
        },

        /**
         * @override
         */
        renderElement: function () {
            this._super();

            let invoiceDueDate = new Date(this.invoice_id.invoice_date_due || this.invoice_id.invoice_date);
            let todayDate = new Date();
            todayDate.setHours(0, 0, 0, 0);

            if (invoiceDueDate <= todayDate) {
                const invoiceStateClass = this.invoice_id.surcharge_amount ? 'overdue' : 'overdue--surcharge-paid';
                this.$el.addClass(invoiceStateClass);
            }
        }

    });

    const PaymentRegisterInvoiceListScreen = PosBaseWidget.extend({
        template: 'PaymentRegister.components.invoiceList',
        events: {},

        /**
         * @override
         * @param parent
         * @param options
         */
        init: function (parent, options) {
            this._super(parent, options);
            this.invoice_row_list = [];
        },

        /**
         * Render a message in the invoice list section
         * @public
         * @param message
         */
        render_message: function (message) {
            let $messageContainer = this.$el.find(".invoice-list__message");
            $messageContainer.removeClass('oe_hidden');
            let $messageContent = this.$el.find(".js_message_content").empty();
            let messageContent = document.createElement("div");
            messageContent.innerHTML = message;
            messageContent.classList.add("background-message");

            $messageContent.append(messageContent);
        },

        /**
         * @override
         * @param reload
         */
        show: function (reload) {

            this._super(reload);
            this.renderElement();
            const partnerId = this.getParent().partner_id;
            if (!partnerId) {
                this.render_message(_t("No customer has been selected"));
                return;
            }
            if (reload) {
                this._rebuild_invoice_rows();
                const invoiceListTbody = this.$el.find('.invoice-list__content');
                if (this.invoice_row_list.length) {
                    _.forEach(this.invoice_row_list, function (invoiceRow) {
                        invoiceListTbody.append(invoiceRow.$el);
                    });
                } else {
                    this.render_message(_.str.sprintf(_t("%s has no due invoice"), partnerId.name));
                }
            }


        },

        /**
         * Rebuild invoice_row_list
         * @private
         */
        _rebuild_invoice_rows: function () {
            this.invoice_row_list = [];
            const self = this;
            _.each(this.getParent().invoice_ids, function (invoice) {
                if (parseFloat(invoice.amount_residual.toFixed(2)) > 0) {
                    const invoiceRow = new InvoiceListRow(this, invoice);
                    invoiceRow.renderElement();
                    self.invoice_row_list.push(invoiceRow);
                }
            });
        }
    });

    return PaymentRegisterInvoiceListScreen;

});
