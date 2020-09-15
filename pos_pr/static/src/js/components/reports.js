odoo.define('pos_pr.components.reports', function (require) {
    'use strict';

    const BaseWidget = require('point_of_sale.BaseWidget');

    const InvoicePaymentReceiptment = BaseWidget.extend({
        template: 'PosPr.InvoicePaymentReceipt',

        /**
         * This will be used to render payments receipts in POS.
         * @param {Object} parent The current parent
         * @param {Object} options Widget's options
         * @param {Object} options.paymentGroup The payment group to rendered
         * @param {Object} options.customer The customer to rendered
         */
        init: function (parent, options) {
            this._super.apply(this, arguments);

            // Attributes by options
            this.paymentGroup = options.paymentGroup || {};
            this.customer = options.customer || {};

            // Default attributes
            this.company = this.pos.company;
            Object.defineProperty(this, 'invoices', {get: this._compute_invoice});
            Object.defineProperty(this, 'payments_by_invoice', {get: this._compute_payments_by_invoice});
            Object.defineProperty(this, 'payment_totals_by_method', {get: this._compute_payment_totals_by_method});
            Object.defineProperty(this, 'payment_methods', {get: this._compute_payment_methods});
        },

        _compute_invoice: function () {
            const invoices = [];
            _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {
                if (!invoices.some(invoice => invoice.id === invoicePayment.move_id.id)) {
                    invoices.push(invoicePayment.move_id);
                }
            });
            return invoices;
        },

        _compute_payment_methods: function () {
            const paymentMethods = [];
            _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {
                if (!paymentMethods.some(paymentMethod => paymentMethod.id === invoicePayment.payment_method_id.id)) {
                    paymentMethods.push(invoicePayment.payment_method_id);
                }
            });
            return paymentMethods;
        },

        _compute_payments_by_invoice: function () {
            const paymentsByInvoice = {};
            _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {

                const invoicePaymentInvoice = invoicePayment.move_id;
                if (!paymentsByInvoice[invoicePaymentInvoice.id]) {
                    paymentsByInvoice[invoicePaymentInvoice.id] = [];
                }
                paymentsByInvoice[invoicePaymentInvoice.id].push(invoicePayment);
            });
            return paymentsByInvoice;
        },

        _compute_payment_totals_by_method: function () {
            const paymentTotalsByMethod = {};
            _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {

                const paymentMethod = invoicePayment.payment_method_id;
                if (!paymentTotalsByMethod[paymentMethod.id]) {
                    paymentTotalsByMethod[paymentMethod.id] = 0;
                }
                paymentTotalsByMethod[paymentMethod.id] += invoicePayment.payment_amount;
            });
            return paymentTotalsByMethod;
        }
    });

    const SurchargePaymentReceiptment = BaseWidget.extend({
        template: 'PosPr.SurchargePaymentReceipt',

        /**
         * This will be used to render payments receipts in POS.
         * @param {Object} parent The current parent
         * @param {Object} options Widget's options
         * @param {Object} options.surcharge The surcharge to rendered
         * @param {Object} options.customer The customer to rendered
         */
        init: function (parent, options) {
            this._super.apply(this, arguments);

            // Attributes by options
            this.surcharge = options.surcharge || {};
            this.customer = options.customer || {};

            // Default attributes
            this.company = this.pos.company;
            // Object.defineProperty(this, 'invoices', {get: this._compute_invoice});
            // Object.defineProperty(this, 'payments_by_invoice', {get: this._compute_payments_by_invoice});
            // Object.defineProperty(this, 'payment_totals_by_method', {get: this._compute_payment_totals_by_method});
            // Object.defineProperty(this, 'payment_methods', {get: this._compute_payment_methods});
        },
        //
        // _compute_invoice: function () {
        //     const invoices = [];
        //     _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {
        //         if (!invoices.some(invoice => invoice.id === invoicePayment.move_id.id)) {
        //             invoices.push(invoicePayment.move_id);
        //         }
        //     });
        //     return invoices;
        // },
        //
        // _compute_payment_methods: function () {
        //     const paymentMethods = [];
        //     _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {
        //         if (!paymentMethods.some(paymentMethod => paymentMethod.id === invoicePayment.payment_method_id.id)) {
        //             paymentMethods.push(invoicePayment.payment_method_id);
        //         }
        //     });
        //     return paymentMethods;
        // },
        //
        // _compute_payments_by_invoice: function () {
        //     const paymentsByInvoice = {};
        //     _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {
        //
        //         const invoicePaymentInvoice = invoicePayment.move_id;
        //         if (!paymentsByInvoice[invoicePaymentInvoice.id]) {
        //             paymentsByInvoice[invoicePaymentInvoice.id] = [];
        //         }
        //         paymentsByInvoice[invoicePaymentInvoice.id].push(invoicePayment);
        //     });
        //     return paymentsByInvoice;
        // },
        //
        // _compute_payment_totals_by_method: function () {
        //     const paymentTotalsByMethod = {};
        //     _.each(this.paymentGroup.invoice_payment_ids, function (invoicePayment) {
        //
        //         const paymentMethod = invoicePayment.payment_method_id;
        //         if (!paymentTotalsByMethod[paymentMethod.id]) {
        //             paymentTotalsByMethod[paymentMethod.id] = 0;
        //         }
        //         paymentTotalsByMethod[paymentMethod.id] += invoicePayment.payment_amount;
        //     });
        //     return paymentTotalsByMethod;
        // }
    });
    return {
        InvoicePaymentReceiptment,
        SurchargePaymentReceiptment,
    };

});
