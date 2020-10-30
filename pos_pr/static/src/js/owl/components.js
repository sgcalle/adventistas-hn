odoo.define('pos_pr.owl.components', function (require) {
    "use strict";

    /*
    * This is used to create all OWL components
    * */
    require('pos_pr.owl.init');
    const {InvoicePayment, PaymentGroup, SurchargeInvoice} = require("pos_pr.models");

    // const {PosWalletPaymentSTComponent, WalletPaymentCardCompoment} = require('pos_wallet.owl.components');
    const {Component, useState} = owl;
    const {verifyInputNumber} = require('eduweb_utils.numbers');

    /*Left Side Invoice List*/
    class PosPRScreenInvoiceListRow extends Component {
        static props = ['pos', 'paymentRegister', 'invoice', 'posPrState'];

        get expected_final_due() {

            let amount_paid = 0;
            // Just a shorter name for this ;)
            const paymentsList = this.props.posPrState.invoicePayments[this.props.invoice.id];
            if (paymentsList) {
                amount_paid = _.reduce(paymentsList, (memo, value) => memo + (value || 0), 0);
            }

            return (this.props.invoice.amount_residual || 0) - amount_paid - (this.props.invoice.discount_amount || 0);
        }

    }

    class PosPRScreenLeftSide extends Component {
        static props = ['pos', 'paymentRegister', 'partner', 'posPrState', 'invoiceList'];
        static components = {PosPRScreenInvoiceListRow};

        selectInvoice(invoice, event) {
            if (invoice.id === this.props.posPrState.selectedInvoice.id) {
                invoice = {};
            } else {
                if (!this.props.posPrState.invoicePayments[invoice.id]) {
                    this.props.posPrState.invoicePayments[invoice.id] = _.chain(this.props.pos.payment_methods).map(paymentMethod => [paymentMethod.id, 0]).object().value();
                }
            }

            this.trigger('select-invoice', invoice);
        }
    }

    /*Right Side Payment dashboard*/
    class PosPRGlobalPaymentDetails extends Component {
        static props = ['pos', 'paymentRegister', 'posPrState', 'surchargeAmount'];

        get computedSurcharge() {
            let amount_paid = 0;
            // Just a shorter name for this x2 ;)
            const paymentsList = this.props.posPrState.globalInvoicesPayment;
            if (paymentsList) {
                amount_paid = _.reduce(paymentsList, (memo, value) => memo + (value || 0), 0);
            }

            return (this.props.surchargeAmount || 0) - amount_paid;
        }

    }

    class PosPRInvoiceDetails extends Component {
        static props = ['pos', 'paymentRegister', 'posPrState'];
    }

    class PosPRPaymentListRow extends Component {
        static props = ['pos', 'paymentRegister', 'paymentMethod', 'posPrState'];

        state = useState({
            paymentAmount: 0,
        })

        /**
         * @param {InputEvent} event
         */
        updateInvoicePaymentAmount(event) {
            const decimals = ((this.pos && this.pos.currency) ? this.pos.currency.decimals : 2) || 2;
            this.props.posPrState.invoicePayments[this.props.posPrState.selectedInvoice.id][this.props.paymentMethod.id] = verifyInputNumber(event.currentTarget, decimals);
        }

        /**
         * @param {InputEvent} event
         */
        updateGlobalPaymentAmount(event) {
            const decimals = ((this.pos && this.pos.currency) ? this.pos.currency.decimals : 2) || 2;
            this.props.posPrState.globalInvoicesPayment[this.props.paymentMethod.id] = verifyInputNumber(event.currentTarget, decimals);
        }
    }

    class PosPRDiscountRow extends Component {
        static props = ['pos', 'paymentRegister', 'posPrState'];
    }

    class PosPRPaymentList extends Component {
        static props = ['pos', 'paymentRegister', 'posPrState'];

        static components = {PosPRPaymentListRow, PosPRDiscountRow};

        state = useState({
            paymentMethods: [{name: 'Hola'}]
        })
    }

    class PosPRScreenRightSide extends Component {
        static props = ['pos', 'paymentRegister', 'posPrState', 'surchargeAmount'];

        static components = {PosPRInvoiceDetails, PosPRGlobalPaymentDetails, PosPRPaymentList};
    }

    /*Screen*/

    class PosPRScreenFilter extends Component {
        static props = ['studentList', 'invoiceAddressList', 'posPrState'];

        /**
         * @param {EventTarget} checkboxElement
         * @param {HTMLInputElement} checkboxElement
         * @param {String} propsListName
         * @param value
         * @private
         */
        _toggleListFilterWithCheckbox(checkboxElement, propsListName, value) {
            const auxList = Array.from(this.props.posPrState[propsListName]);
            if (checkboxElement.checked) {
                auxList.push(value);
            } else {
                const index = _.indexOf(auxList, value);
                if (index > -1) {
                    auxList.splice(index, 1);
                }
            }
            this.props.posPrState[propsListName] = auxList;
        }

        /**
         * @param {Number} studentId
         * @param {InputEvent} event
         */
        toggleStudentFilter(studentId, event) {
            this._toggleListFilterWithCheckbox(event.currentTarget, 'filterStudentsIds', studentId);
        }

        /**
         * @param {Number} invoiceAddressId
         * @param {InputEvent} event
         */
        togglePartnerFilter(invoiceAddressId, event) {
            this._toggleListFilterWithCheckbox(event.currentTarget, 'filterPartnerIds', invoiceAddressId);
        }
    }

    class PosPRScreen extends Component {
        // Properties
        static props = ['pos', 'paymentRegister'];
        static components = {PosPRScreenLeftSide, PosPRScreenRightSide, PosPRScreenFilter};

        state = useState({
            partner: {},
            selectedInvoice: {},
            invoicePayments: {},
            globalInvoicesPayment: _.chain(this.props.pos.payment_methods).map(paymentMethod => [paymentMethod.id, 0]).object().value(),
            showScreen: false,
            filterStudentsIds: [],
            filterPartnerIds: [],
            selectedInvoiceAddress: 0,
            payWithWalletButton: null,
            extraPayments: [],
        });

        // We use this just for patched method
        // We need it in order to no create a infity loop using an simple if
        previousPartner = {};

        // Getters
        get invoiceList() {
            if (this.state && this.state.partner) {
                return this.props.pos.db.due_invoices.filter(invoice =>
                    (invoice.partner_id.id === this.state.partner.id
                        // We use this fields for the schools.
                        // TODO: Move this to a future pos_pr_school module
                        || (invoice.student_id && invoice.student_id.id === this.state.partner.id)
                        || (invoice.family_id && invoice.family_id.id === this.state.partner.id))

                    // We need only the due invoices
                    && invoice.amount_residual > 0
                );
            } else {
                return [];
            }
        }

        get filteredInvoiceList() {
            const filteredInvoiceList = this.invoiceList.filter(invoice =>
                (!this.state.filterStudentsIds.length || _.indexOf(this.state.filterStudentsIds, invoice.student_id.id) !== -1)
                && (!this.state.filterPartnerIds.length || _.indexOf(this.state.filterPartnerIds, invoice.partner_id.id) !== -1)
            );
            return filteredInvoiceList;
        }

        get studentList() {
            const invoiceList = this.invoiceList;
            if (invoiceList) {
                return _.chain(invoiceList).map(invoice => invoice.student_id).uniq(false, student => student.id).value();
            } else {
                return [];
            }
        }

        get invoiceAddressList() {
            return this.state.partner ? _.map(this.state.partner.student_invoice_address_ids, partnerId => this.props.pos.db.partner_by_id[partnerId]) : [];
        }

        get invoicesPartnerList() {
            const invoiceList = this.invoiceList;
            if (invoiceList) {
                return _.chain(invoiceList).map(invoice => invoice.partner_id).uniq(false, partner => partner.id).value();
            } else {
                return [];
            }
        }

        get surchargeAmount() {
            const surchargeAmount = _.reduce(this.filteredInvoiceList.filter(inv => inv.surcharge_amount), (memo, inv) => memo + inv.surcharge_amount, 0) || 0;
            return surchargeAmount;
        }

        getExpectedAmountDue(invoice) {
            let amount_paid = 0;
            // Just a shorter name for this x3 ;)
            const paymentsList = this.state.invoicePayments[invoice.id];
            if (paymentsList) {
                amount_paid = _.reduce(paymentsList, (memo, value) => memo + (value || 0), 0);
            }

            return (invoice.amount_residual || 0) - amount_paid - (invoice.discount_amount || 0);
        }

        /**
         * @param {Event} event
         */
        selectInvoiceAddress(event) {
            const selectInvoiceAddressId = parseInt(event.currentTarget.value) || 0;
            this.state.selectedInvoiceAddress = _.find(this.invoiceAddressList, invAddress => invAddress.id === selectInvoiceAddressId);
        }

        patched() {
            super.patched();
            // If they are different, that means that the partner has changed
            if (this.previousPartner !== this.state.partner) {
                this.state.selectedInvoiceAddress = this.invoiceAddressList.length ? this.invoiceAddressList[0] : {};
                this.previousPartner = this.state.partner;
            }
            console.log('this.state.partner.name: ' + this.state.partner.name);
        }

        // Methods
        /**
         * @param {MouseEvent} event
         */
        toggleFilter(event) {

            const button = event.currentTarget;
            button.classList.toggle('toggle-screen-filter-button--active')

            this.state.showScreen = !this.state.showScreen;
        }

        /**
         * @param {OwlEvent} event
         */
        selectInvoice(event) {
            this.state.selectedInvoice = event.detail || {};
        }

        _updateInvoicesAmounts(invoicePayments) {
            _.each(invoicePayments, invoicePayment => {
                const invoice = invoicePayment.move_id;
                const paymentMethod = invoicePayment.payment_method_id;

                // We reset the value because the payment is success at this point
                this.state.invoicePayments[invoice.id][paymentMethod.id] = 0;
                invoice.amount_residual -= invoicePayment.payment_amount + invoicePayment.discount_amount;
            })
        }

        validatePayments() {
            const invoicePayments = this._createInvoicePayments();

            this._updateInvoicesAmounts(invoicePayments);

            if (invoicePayments && invoicePayments.length > 0) {
                const paymentGroup = new PaymentGroup({
                    'name': this.props.pos.generateNextPaymentGroupNumber(),
                    'invoice_payment_ids': invoicePayments
                });

                this.props.pos.gui.show_screen('invoicePaymentReceipt', {
                    paymentGroup,
                    invoiceAddress: this.state.selectedInvoiceAddress || this.state.partner,
                });
                this.state.extraPayments = [];
                this.props.pos.synch_invoive_payment_and_surcharges(paymentGroup, []);

                // _.each(self.invoice_ids, function (invoice) {
                //     self._deselect_invoice();
                //     invoice.amount_residual = invoice.expected_final_due;
                //     invoice.discount_amount = 0;
                //     _.each(self.pos.payment_methods, function (paymentMethod) {
                //         self._update_invoice_payment_amount(invoice.id, paymentMethod.id, 0);
                //     });
                // });
            }
        }

        validateSurchargePayments() {
            const surcharge = this._createAndPayInvoicesSurcharge();
            console.log(surcharge);
            this.props.pos.gui.show_screen('surchargePaymentReceipt', {
                surcharge,
                invoiceAddress: this.state.selectedInvoiceAddress
            });
            this.props.pos.synch_invoive_payment_and_surcharges([], [surcharge]);
        }

        /**
         * Create a invoicePayment with the params
         * @param {{paymentMethod: *, invoiceAddress: (number|*|{}), invoice: ({}|{records: [{id: number, invoice_line_ids: number[]}], fields: {invoice_line_ids: {string: string, relation_field: string, type: string, relation: string}}}|Object), paymentAmount: *}} properties
         * @param {Object} properties.invoice
         * @param {Object|Number} properties.paymentMethod
         * @param {Number} properties.paymentAmount
         * @param {Number} properties.paymentDiscount
         * @param {Object} properties.invoiceAddress
         * @returns {Object}
         * @private
         */
        _createInvoicePaymentObject(properties) {
            const invoicePayment = new InvoicePayment;

            invoicePayment.name = this.props.pos.generateNextPaymentNumber();
            invoicePayment.date = moment().format('YYYY-MM-DD HH:mm:ss');
            invoicePayment.move_id = properties.invoice;
            invoicePayment.invoice_address_id = properties.invoiceAddress;
            invoicePayment.pos_session_id = this.props.pos.pos_session.id;
            invoicePayment.payment_method_id = properties.paymentMethod;

            invoicePayment.payment_amount = properties.paymentAmount;
            invoicePayment.discount_amount = properties.paymentDiscount || 0;

            return invoicePayment;
        };

        /**
         * Create a array of invoice payments object based on the state.invoicePayments field
         * @returns {[]}
         */
        _createInvoicePayments() {
            const invoicePaymentList = this.state.extraPayments;

            // We get this with a getter
            if (this.invoiceList) {
                _.each(this.invoiceList, (invoice) => {
                    const invoicePaymentAmounts = this.state.invoicePayments[invoice.id];

                    // We use these guys for the reports
                    invoice.last_amount_residual = invoice.amount_residual;
                    invoice.last_discount_amount = invoice.discount_amount;

                    // We check if there is some payment in the invoice

                    if (invoicePaymentAmounts) {
                        _.each(this.props.pos.payment_methods, (paymentMethod) => {
                            // Then we create a payment for every no zero payment in the state.invoicePayments object
                            let invoicePaymentAmount = invoicePaymentAmounts[paymentMethod.id];
                            if (invoicePaymentAmount > 0) {

                                const invoicePayment = this._createInvoicePaymentObject({
                                    invoice,
                                    paymentMethod,
                                    paymentAmount: invoicePaymentAmounts[paymentMethod.id],
                                    invoiceAddress: this.state.selectedInvoiceAddress || this.state.partner,
                                });

                                // And we feed the return array with the new created InvoicePayment Object
                                invoicePaymentList.push(invoicePayment);
                            }
                        });
                    }

                    // Check if we have some discount
                    // We are going to pass the discount as an payment without payment method
                    if (invoice.discount_amount) {
                        const paymentMethod = this.props.pos.db.discount_payment_method;
                        const invoicePayment = this._createInvoicePaymentObject({
                                invoice,
                                paymentMethod,
                                paymentAmount: 0,
                                paymentDiscount: parseFloat(invoice.discount_amount)
                            }
                        );
                        // invoice.amount_residual -= invoice.discount_amount;
                        invoice.discount_amount = 0;

                        invoicePaymentList.push(invoicePayment);
                    }
                });

            }

            return invoicePaymentList;
        }

        /**
         * Create an surcharge payment
         */
        _createGenericSurcharge() {
            const surcharge = new SurchargeInvoice;
            surcharge.date = moment().format('YYYY-MM-DD HH:mm:ss');
            surcharge.pos_session_id = this.props.pos.pos_session.id;
            surcharge.partner_id = this.state.partner.person_type === 'student' ? this.props.pos.db.partner_by_id[this.state.selectedInvoiceAddressId] : this.state.partner;
            surcharge.free_of_surcharge = 0;
            surcharge.amount = 0;
            // surcharge.free_of_surcharge = (this.free_of_surcharge[this.partner_id.id] || 0) || 0;

            // let surchargePaymentInvoiceIds = this._clear_all_invoices_surcharge(surcharge);
            // this._append_payments_to_surcharge(surcharge, surchargePaymentInvoiceIds);

            return surcharge;
        }

        applyGlobalPaymentsToInvoices() {
            // We need break and continue for code efficiency
            // For that reason we don't use _.each
            for (const walletId in this.state.globalInvoicesPayment) {
                if (Object.prototype.hasOwnProperty.call(this.state.globalInvoicesPayment, walletId)) {
                    let amount = this.state.globalInvoicesPayment[walletId];
                    for (const invoice of this.filteredInvoiceList) {
                        const invoiceExpectedAmountDue = this.getExpectedAmountDue(invoice);
                        if (invoiceExpectedAmountDue) {
                            const amountToPay = Math.min(amount, invoiceExpectedAmountDue);

                            // Just in case there isn't some of these setted before
                            if (!this.state.invoicePayments[invoice.id]) {
                                this.state.invoicePayments[invoice.id] = {};
                            }

                            if (!this.state.invoicePayments[invoice.id][walletId]) {
                                this.state.invoicePayments[invoice.id][walletId] = 0;
                            }

                            this.state.invoicePayments[invoice.id][walletId] += amountToPay;
                            this.state.globalInvoicesPayment[walletId] -= amountToPay;
                            amount = amount - amountToPay;

                            // Skip if there is no more
                            if (!amount) {
                                break;
                            }
                        }
                    }
                }
            }


            // _.each(this.state.globalInvoicesPayment, (amount, walletId) => {
            //     const surchargeToPay = Math.min(amount, invoice.surcharge_amount);
            //     invoice.surcharge_amount -= surchargeToPay;
            //     this.state.globalInvoicesPayment[walletId] -= surchargeToPay;
            // })
        }

        _createAndPayInvoicesSurcharge() {
            const surcharge = this._createGenericSurcharge();

            // Invoice surcharge payment
            // Pay locally the surcharge with the payments
            // and we store and sum the amounts into invoiceAmountPaidByMethod
            const invoiceAmountPaidByMethod = {};
            _.chain(this.filteredInvoiceList)
                .filter(invoice => invoice.surcharge_amount > 0)
                .each(invoice => {
                    // Trying to pay
                    invoice.last_surcharge_amount = invoice.surcharge_amount;
                    _.each(this.state.globalInvoicesPayment, (amount, walletId) => {
                        const surchargeToPay = Math.min(amount, invoice.surcharge_amount);
                        if (surchargeToPay > 0) {
                            invoice.surcharge_amount -= surchargeToPay;
                            this.state.globalInvoicesPayment[walletId] -= surchargeToPay;
                            invoiceAmountPaidByMethod[walletId] = (invoiceAmountPaidByMethod[walletId] || 0) + surchargeToPay

                            if (!_.find(surcharge.move_ids, move => move === invoice)) {
                                surcharge.move_ids.push(invoice);
                            }
                        }
                    })
                });

            // Payment creation
            _.each(invoiceAmountPaidByMethod, (amount, paymentMethodId) => {

                const paymentMethod = this.props.pos.payment_methods_by_id[paymentMethodId];

                let invoicePayment = this._createInvoicePaymentObject({
                    paymentAmount: amount,
                    paymentMethod: paymentMethod,
                    invoiceAddress: this.state.selectedInvoiceAddress || this.state.partner,
                });
                surcharge.amount += amount;
                surcharge.payment_ids.push(invoicePayment);
            });

            return surcharge;
        }
    }

    return {
        PosPRScreen,
    };

});