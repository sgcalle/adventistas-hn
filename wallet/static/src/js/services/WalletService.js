odoo.define('wallet.services.WalletService', function (require) {

    const AbstractService = require('web.AbstractService');
    const core = require('web.core');

    const rpc = require('web.rpc');
    const walletModels = require('wallet.models');

    const _t = core._t;

    return rpc.query({
        model: 'wallet.category',
        method: 'search_read',
        fields: [
            'id',
            'name',
            'category_id',
            'parent_wallet_id',
            'parent_wallet_count',
            'child_wallet_ids',
            'is_default_wallet',
        ],
        domain: []
    }).then(wallets => {
        const WalletService = AbstractService.extend({
            name: 'WalletService',

            init: function () {
                this._super.apply(this, arguments);
                this.wallets = [];
                this.wallets_by_id = {};
                this.default_wallet = {};

                _.each(wallets, walletOdoo => {
                    const wallet = new walletModels.WalletCategoryBuilder()
                        .setId(walletOdoo.id)
                        .setName(walletOdoo.name)
                        .setCategory({id: walletOdoo.category_id[0], name: walletOdoo.category_id[1]})
                        .setParentWallet({id: walletOdoo.parent_wallet_id[0], name: walletOdoo.parent_wallet_id[1]})
                        .setParentWalletCount(walletOdoo.parent_wallet_count)
                        .setChildWallets(walletOdoo.child_wallet_ids)
                        .setIsDefaultWallet(walletOdoo.is_default_wallet)
                        .build();
                    this.wallets.push(wallet);
                    this.wallets_by_id[wallet.id] = wallet;

                    if (wallet.is_default_wallet) {
                        this.default_wallet = wallet;
                    }

                });
                console.log(this.wallets);
            },

            getWallets: function () {
                return this.wallets;
            },

            getDefaultWallet: function () {
                return this.default_wallet;
            },

            getWalletById: function (walletId) {
                return this.wallets_by_id[walletId];
            },

            loadWalletWithPayment: async function (partner_id, wallet_id, amount) {
                if (wallet_id && typeof (wallet_id) === 'number' && wallet_id in this.wallets_by_id) {
                    console.log(`Added: ${partner_id}, to ${this.wallets_by_id[wallet_id].name} the amount of ${amount}`)
                } else {
                    throw Error(_.str.sprintf(_t("Wallet with id: %s not found", wallet_id)));
                }
            }
        });

        core.serviceRegistry.add('WalletService', WalletService);
        return WalletService;
    })
})