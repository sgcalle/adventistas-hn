odoo.define('pos_pr.load_data.pos_config', function (require) {

    const models = require('point_of_sale.models');
    models.load_fields('pos.session', ['invoice_surcharge_ids', 'invoice_payment_ids', 'invoice_payment_groups_ids']);
    models.load_fields('res.company', ['city', 'street']);

    models.PosModel = models.PosModel.extend({

        /**
         * Get the tCurrent number in the payment sequence
         * @param {Boolean} reset Reset the payment sequence
         */
        getCurrentPaymentSequenceNumber: function (reset) {
            reset = !!reset;
            let paymentSequenceNumber = parseInt(this.db.load('payment_sequence_number', 0));
            if (!paymentSequenceNumber || reset) {
                paymentSequenceNumber = this.pos_session.invoice_payment_ids.length;
            }
            this.db.save('payment_sequence_number', paymentSequenceNumber);
            return paymentSequenceNumber;
        },

        /**
         * Get the next number in the payment sequence
         * @param {Boolean} [reset] Reset the payment sequence
         */
        getNextPaymentSequenceNumber: function (reset) {
            reset = !!reset;
            const nextNumber = this.getCurrentPaymentSequenceNumber(reset) + 1;
            this.db.save('payment_sequence_number', nextNumber);
            return nextNumber;
        },


        /**
         * Get the tCurrent number in the payment group sequence
         * @param {Boolean} reset Reset the payment group sequence
         */
        getCurrentPaymentGroupSequenceNumber: function (reset) {
            reset = !!reset;
            let paymentSequenceNumber = parseInt(this.db.load('payment_group_sequence_number', 0));

            if (!paymentSequenceNumber || reset) {
                paymentSequenceNumber = this.pos_session.invoice_payment_groups_ids.length;
            }
            this.db.save('payment_group_sequence_number', paymentSequenceNumber);
            return paymentSequenceNumber;

        },

        /**
         * Get the next number in the payment group sequence
         * @param {Boolean} [reset] reset Reset the payment group sequence
         */
        getNextPaymentGroupSequenceNumber: function (reset) {
            reset = !!reset;
            const nextNumber = this.getCurrentPaymentGroupSequenceNumber(reset) + 1;
            this.db.save('payment_group_sequence_number', nextNumber);
            return nextNumber;
        },

        generateNextPaymentNumber: function () {
            const nextNumber = this.getNextPaymentSequenceNumber();
            return 'POS-P/'
                + this._zero_pad(this.pos_session.id, 5) + '-'
                + this._zero_pad(this.pos_session.login_number, 3) + '/'
                + this._zero_pad(nextNumber, 5);
        },

        generateNextPaymentGroupNumber: function () {
            const nextNumber = this.getNextPaymentGroupSequenceNumber();
            return 'POS-PG/'
                + this._zero_pad(this.pos_session.id, 5) + '-'
                + this._zero_pad(this.pos_session.login_number, 3) + '/'
                + this._zero_pad(nextNumber, 5);
        },

        _zero_pad: function (num, size) {
            let s = "" + num;
            while (s.length < size) {
                s = "0" + s;
            }
            return s;
        },

        /**
         * Get the company with a specific format
         */
        getFormattedCompanyAddress: function () {

            let formattedCompanyAddress = "";
            if (this.company.country) {
                formattedCompanyAddress += this.company.country.name + ', ';
            }
            if (this.company.state_id) {
                formattedCompanyAddress += this.company.state_id[1] + ', ';
            }
            if (this.company.city) {
                formattedCompanyAddress += this.company.city + ', ';
            }
            if (this.company.street) {
                formattedCompanyAddress += this.company.street;
            }
            formattedCompanyAddress = formattedCompanyAddress.trim().replace('/,$/', '');
            return formattedCompanyAddress;
        }
    });

});
