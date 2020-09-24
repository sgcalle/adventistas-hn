odoo.define('wallet.models', function (require) {

    const Class = require('web.Class');

    const WalletCategory = Class.extend({

        init: function (id, name, category) {
            this.id = id;
            this.name = name;
            this.category = category;
        }
    });

    /**
     * We want a builder to improve readability
     */
    const WalletCategoryBuilder = Class.extend({

        init: function () {
            this.id = undefined;
            this.name = '';
            this.category = {};
        },

        setId: function (id) {
            this.id = id;
            return this;
        },

        setName: function (name) {
            this.name = name;
            return this;
        },

        setCategory: function (category) {
            this.category = category;
            return this;
        },

        build: function() {
            return new WalletCategory(this.id, this.name, this.category)
        }
    });

    return {
        WalletCategory: WalletCategory,
        WalletCategoryBuilder: WalletCategoryBuilder,
    };
})