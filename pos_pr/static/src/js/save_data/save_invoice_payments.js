odoo.define("pos_pr.save_invoice_payments", function (require) {

    const models = require("point_of_sale.models");
    const rpc = require('web.rpc');

    const core = require("web.core");
    const _t = core._t;

    const PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function () {
            PosModelSuper.prototype.initialize.apply(this, arguments);
            const self = this;
            this.ready.then(function () {
                const pendingInvoicePayments = self.db.load('pending_invoice_payments', []);
                const pendingSurchargeInvoices = self.db.load('pending_surcharge_invoices', []);

                self.db.save('pending_invoice_payments', pendingInvoicePayments);
                self.db.save('pending_surcharge_invoices', pendingSurchargeInvoices);
            });
        },

        send_surcharge: function (surchargesAsJson) {
            return new Promise((resolve, reject) => {
                if (surchargesAsJson && surchargesAsJson.length) {

                    rpc.query({
                        model: "pos_pr.invoice.surcharge",
                        method: "create",
                        args: [surchargesAsJson]
                    }, {}).then(function () {
                        resolve();
                    }).catch(function () {
                        reject();
                    });
                } else {
                    resolve();
                }
            });
        },


        send_invoice_payments: function (invoicePaymentsJson) {
            return new Promise(function (resolve, reject) {
                if (invoicePaymentsJson && invoicePaymentsJson.length) {
                    rpc.query({
                        model: "pos_pr.invoice.payment",
                        method: "create",
                        args: [invoicePaymentsJson],
                    }, {}).then(function () {
                        resolve();
                    }).catch(function () {
                        reject();
                    });
                } else {
                    resolve();
                }
            });
        },

        synch_invoive_payment_and_surcharges(invoicePayments, surcharges) {
            const self = this;
            invoicePayments = invoicePayments || [];
            surcharges = surcharges || [];

            let newSurchargesJSON = [];
            let newInvoicePaymentsJSON = [];

            if (invoicePayments && invoicePayments.length > 0) {
                newInvoicePaymentsJSON = invoicePayments.map((payment) => payment.export_as_JSON());
            }

            if (surcharges && surcharges.length > 0) {
                for (let i = 0; i < surcharges.length; i++) {
                    const surcharge = surcharges[i];
                    const surchargeJSON = surcharge.export_as_JSON();
                    surchargeJSON.payment_ids = surcharge.payment_ids.map((payment) => [0, 0, payment.export_as_JSON()]);
                    newSurchargesJSON.push(surchargeJSON);
                }
            }

            const pendingInvoicePayments = this.db.load('pending_invoice_payments', []);
            const pendingSurchargeInvoices = this.db.load('pending_surcharge_invoices', []);

            const surchargesToSynch = pendingSurchargeInvoices.concat(newSurchargesJSON);
            const invoicePaymentsToSynch = pendingInvoicePayments.concat(newInvoicePaymentsJSON);

            this.db.save('pending_invoice_payments', []);
            this.db.save('pending_surcharge_invoices', []);

            this.trigger('invoice_payment:synch', {
                'state': 'connecting',
                'pending': surchargesToSynch.length + invoicePaymentsToSynch.length,
            });

            if (surchargesToSynch.length > 0 || invoicePaymentsToSynch.length > 0) {
                Promise.all([this.send_surcharge(surchargesToSynch), this.send_invoice_payments(invoicePaymentsToSynch)])
                    .then(function () {
                        self.trigger('invoice_payment:synch', {
                            'state': 'connected',
                        });
                        self.gui.show_popup('alert', {
                            'title': _t('Changes saved correctly'),
                            'body': _t('In order to apply the changes in backend the Point of sale needs to be closed and validated'),
                        });
                    }).catch(function (error, a, b, c) {
                    console.error(error, a, b, c);
                    self.trigger('invoice_payment:synch', {
                        'state': 'disconnected',
                        'pending': surchargesToSynch.length + invoicePaymentsToSynch.length,
                    });
                    self.gui.show_popup('error-sync', {
                        'title': _t('Changes could not be saved'),
                        'body': _t('You need to be connected to validate the changes'),
                    });
                    self.db.save('pending_invoice_payments', invoicePaymentsToSynch);
                    self.db.save('pending_surcharge_invoices', surchargesToSynch);
                });
            }
        },
    });

});
