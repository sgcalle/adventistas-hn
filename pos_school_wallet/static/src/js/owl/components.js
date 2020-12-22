odoo.define("pos_wallet_school.components", function (require) {

    const {PosWalletLoadWalletComponent, LoadWalletPopup} = require('pos_wallet.popups');
    const {useState, Component} = owl;


    //
    // PosWalletLoadWalletComponent.prototype.constructor = function () {
    //     parentConstructor.apply(this, arguments);
    //     this.hola = 'Hola';
    // };

    Object.defineProperty(PosWalletLoadWalletComponent.prototype, 'schoolState', {
        get: function () {
            if (!this._schoolState) {
                this._schoolState = useState({
                    selectedInvoiceAddress: 0,
                    selectedFamily: 0,
                });
            }
            return this._schoolState;
        }
    });

    Object.defineProperty(PosWalletLoadWalletComponent.prototype, 'invoiceAddressList', {
        get: function () {
            const self = this;
            return this.props.pos.get_client() ? _.map(this.props.pos.get_client().student_invoice_address_ids, partnerId => self.props.pos.db.partner_by_id[partnerId]) : [];
        }
    });

    Object.defineProperty(PosWalletLoadWalletComponent.prototype, 'familyRelatedByInvoiceAddressList', {
        get: function () {
            const self = this;
            // console.log('Random coment')
            return this.schoolState.selectedInvoiceAddress ? _.chain(this.schoolState.selectedInvoiceAddress.related_families_by_inv_address_ids)
                .filter(familyId => self.props.pos.get_client().family_ids.indexOf(familyId) !== -1)
                .map(familyId => self.props.pos.db.partner_by_id[familyId]).value() : [];
        }
    })

    PosWalletLoadWalletComponent.prototype.selectInvoiceAddress = function (event) {
        const selectInvoiceAddressId = parseInt(event.currentTarget.value) || 0;
        this.schoolState.selectedInvoiceAddress = _.find(this.invoiceAddressList, invAddress => invAddress.id === selectInvoiceAddressId);
    }

    PosWalletLoadWalletComponent.prototype.selectFamily = function (event) {
        const selectedFamilyId = parseInt(event.currentTarget.value) || 0;
        this.schoolState.selectedFamily = _.find(this.familyRelatedByInvoiceAddressList, family => family.id === selectedFamilyId);
    }

    LoadWalletPopup.include({
        show: function () {
            if (this.pos.get_client()) {

                const invoiceAddressList = this.posWalletLoadWalletComponent.invoiceAddressList;
                this.posWalletLoadWalletComponent.schoolState.selectedInvoiceAddress = invoiceAddressList.length ? invoiceAddressList[0] : {};

                const familyRelatedByInvoiceAddressList = this.posWalletLoadWalletComponent.familyRelatedByInvoiceAddressList;
                this.posWalletLoadWalletComponent.schoolState.selectedFamily = familyRelatedByInvoiceAddressList.length ? familyRelatedByInvoiceAddressList[0] : {};
            }
            this._super.apply(this, arguments);
        },

        _build_load_wallet_options: function () {

            let options = this._super.apply(this, arguments);

            if (this.pos.get_client() && this.pos.get_client().person_type === 'student') {

                options = _.extend({}, options, {
                    student: this.pos.get_client(),
                    family: this.posWalletLoadWalletComponent.schoolState.selectedFamily,
                });

                options.partner_id = this.posWalletLoadWalletComponent.schoolState.selectedInvoiceAddress.id
            }
            return options
        }
    });
});
