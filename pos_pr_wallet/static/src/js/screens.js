odoo.define("pos_pr_wallet.payment_register.screen", function (require) {

    const PosPosPRWidget = require('pos_pr.payment_register.screen');
    const {PayWithWalletButton} = require('pos_pr_wallet.owl.components');

    PosPosPRWidget.include({

        renderElement: function () {
            this._super.apply(this, arguments);
            this.invoicePaymentRegisterScreen.state.payWithWalletButton = PayWithWalletButton;
        }
    });

    // const SuperInvoicePaymentReceiptScreenWidget = InvoicePaymentReceiptScreenWidget;
    // InvoicePaymentReceiptScreenWidget.include({
    //     events: _.extend({}, SuperInvoicePaymentReceiptScreenWidget.prototype.events, {
    //         'click .load-to-wallet': 'loadToWallet',
    //     }),
    //
    //     loadToWallet: function (event) {
    //         const walletList = this.pos.config.wallet_category_ids.map(wallet_id => this.call('WalletService', 'getWalletById', wallet_id));
    //         this.pos.gui.show_popup('posPrWalletLoadWithChange', {
    //             title: _t('Load wallet'),
    //             body: _t('Testing wallet'),
    //         });
    //     }
    //
    //
    // });

});
