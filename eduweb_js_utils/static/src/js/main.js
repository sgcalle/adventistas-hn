odoo.define('eduweb_utils.Class', function (require) {

    const Class = require('web.Class');

    /**
     * This provides new properties to help us build odoo objects
     *
     * API:
     *
     * @field field: An object with the form:
     * {
     *     <column-name>: {
     *         type: <column-type>,
     *         default: <default-value-if-not-exists>,
     *     },
     *     ...
     * }
     * this will be used by init to build automatically the objects
     *
     * allowed types:
     * integer, float, boolean, char, many2one.
     * The rest of the fields will be just set plain without any special format
     *
     * @field model: This will be used by init to build a object for relation fields
     */
    const EduwebClass = Class.extend({

        /**
         * It converts odoo rpc json to a javascript object
         * @param odooJson A json from a RPC odoo call
         * @public
         */
        init: function (odooJson) {
            if (!odooJson) {
                odooJson = {};
            }

            if (this.fields && typeof (this.fields) == 'object') {
                _.each(this.fields, (fieldDescription, fieldName) => {
                    if (Object.hasOwnProperty.call(odooJson, fieldName)) {
                        
                        const jsonFieldValue = odooJson[fieldName];
                        
                        switch (fieldDescription.type) {
                            case 'intenger':
                                this[fieldName] = parseInt(jsonFieldValue);
                                break;
                            case 'float':
                                this[fieldName] = parseFloat(jsonFieldValue);
                                break;
                            case 'boolean':
                                this[fieldName] = !!jsonFieldValue;
                                break;
                            case 'char':
                                this[fieldName] = "" + jsonFieldValue;
                                break;
                            case 'many2one':
                                this[fieldName] = {
                                    id: parseInt(jsonFieldValue[0]),
                                    name: jsonFieldValue[1],
                                };
                                break;
                            default:
                                this[fieldName] = jsonFieldValue;
                                break;
                        }
                    } else {
                        this[fieldName] = fieldDescription.default || this._get_default_field_type_value(fieldDescription.type);
                    }
                });
            }
        },

        /**
         * Odoo get default fields
         * @private
         */
        _get_default_field_type_value: function (fieldType) {
            let defaultValue = null;

            switch (fieldType) {
                case 'char':
                    defaultValue = '';
                    break;
                case 'intenger':
                case 'float':
                    defaultValue = 0;
                    break;
                case 'boolean':
                    defaultValue = false;
                    break;
                case 'selection':
                case 'many2one':
                    defaultValue = null;
                    break;
                case 'many2many':
                case 'one2many':
                    defaultValue = [];
                    break;
            }

            return defaultValue;
        },


    });

    return EduwebClass;

});

odoo.define('eduweb_utils', function (require) {

    const NumberInput = require('eduweb_utils.NumberInput');
    const EduwebClass = require('eduweb_utils.Class');

    return {
        'NumberInput': NumberInput,
        'Class': EduwebClass,
    };
});
