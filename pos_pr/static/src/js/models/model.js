odoo.define('pos_pr.models', function (require) {
    let models = {};

    const EduwebClass = require('eduweb_utils.Class');

    const exportAsJSON = function (object, fields) {
        const jsonObject = {};
        for (const field of fields) {
            jsonObject[field] = object[field];
        }
        return jsonObject;
    };

    const initAsJSON = function (object, fields, json) {
        for (const field of fields) {
            object[field] = json[field];
        }
    };

    models.AccountMove = EduwebClass.extend({

        fields: {
            'id': {type: 'integer'},

            'name': {type: 'char'},


            'amount_total': {type: 'float'},
            'amount_residual': {type: 'float'},
            'session_payment': {type: 'float'},
            'expected_final_due': {type: 'float'},
            'pos_pr_paid_amount': {type: 'float'},
            'surcharge_amount': {type: 'float'},

            'invoice_date': {type: 'date'},
            'invoice_date_due': {type: 'date'},

            'partner_id': {type: 'many2one'},
            'journal_id': {type: 'many2one'},
            'student_id': {type: 'many2one'},
            'family_id': {type: 'many2one'},

            'invoice_line_ids': {type: 'one2many'},
        },

        init_from_JSON: function (json) {
            this.id = json.id;
            this.name = json.name || '/';
            this.partner_id = json.partner_id || false;
            this.journal_id = json.journal_id || false;
            this.invoice_date = json.invoice_date || false;
            this.invoice_date_due = json.invoice_date_due || false;
            this.amount_total = json.amount_total || false;
            this.amount_residual = json.amount_residual || 0;
            this.session_payment = json.session_payment || 0;

            this.expected_final_due = json.expected_final_due || 0;

            this.invoice_line_ids = json.invoice_line_ids || [];

            this.student_id = json.student_id || false;
            this.family_id = json.family_id || false;
        },
        export_as_JSON: function () {
            return {
                id: this.id,
                name: this.name,
                partner_id: this.partner_id,
                student_id: this.student_id,
                family_id: this.family_id,
                journal_id: this.journal_id,
                invoice_line_ids: this.invoice_line_ids,
            };
        },
    });

    models.AccountMoveLine = Backbone.Model.extend({
        constructor: function (invoiceValues) {
            this.init_from_JSON(invoiceValues);
        },
        init_from_JSON: function (json) {
            this.id = json.id;
            this.move_id = json.move_id;
            this.price_unit = json.price_unit;
        },
        export_as_JSON: function () {
            return {
                id: this.id,
                name: this.name,
                partner_id: this.partner_id,
                student_id: this.student_id,
                family_id: this.family_id,
                price_unit: this.price_unit,
            };
        },
    });

    models.InvoicePayment = Backbone.Model.extend({

        fields: ["id", "date", "move_id", "payment_amount", "payment_method_id", "pos_session_id", "discount_amount"],

        init_from_JSON: function (json) {
            initAsJSON(this, this.fields, json);
        },
        export_as_JSON: function () {
            return exportAsJSON(this, this.fields);
        },
    });

    models.SurchargeInvoice = Backbone.Model.extend({

        constructor: function () {
            this.move_ids = [];
            this.payment_ids = [];
            this.amount = 0;
            this.free_of_surcharge = 0;
            Backbone.Model.apply(this, arguments);
        },

        init_from_JSON: function (json) {
            this.id = json.id;
            this.date = json.date;
            this.move_ids = json.move_ids;
            this.amount = json.amount;
            this.payment_ids = json.payment_ids;
            this.free_of_surcharge = json.free_of_surcharge;
            this.pos_session_id = json.pos_session_id;
        },
        export_as_JSON: function () {
            return {
                id: this.id,
                date: this.date,
                move_ids: this.move_ids,
                amount: this.amount,
                free_of_surcharge: this.free_of_surcharge,
                payment_ids: this.payment_ids.map(payment => payment.id),
                pos_session_id: this.pos_session_id,
            };
        },
    });

    models.PaymentRegisterPadState = Backbone.Model.extend({
        constructor: function (payment_method_ids) {
            this.surcharger_amount = 0;
            this.payment_method_ids = payment_method_ids;
            this.payment_amount_by_method_id = {};
            this._generate_paymenta_amounts();
        },

        _generate_paymenta_amounts: function () {
            _.each(this.payment_method_ids, payment_method_id => {
                this.payment_amount_by_method_id[payment_method_id.id] = 0;
            });
        },

    });

    models.PaymentRegisterState = Backbone.Model.extend({});

    return models;

});
