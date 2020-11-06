odoo.define('pos_wallet.owl.components', function (require) {

    require('pos_wallet.owl.init');

    // OWL
    const {Component} = owl;
    const {useState, useDispatch, useStore, useRef} = owl.hooks;
    const walletServiceDepenency = require('wallet.services.WalletService');

    const AutoCompleteInput = require('eduweb_utils.AutoCompleteInput');
    const {_t} = require("web.core");
    const store = require('pos_wallet.owl.store');
    const {Paymentline} = require('point_of_sale.models');

    const {verifyInputNumber} = require('eduweb_utils.numbers');

    // Load
    class PosWalletPartnerScreenComponent extends Component {
        static props = ['pos'];

        state = useState({
            autoCompleteInput: {}
        })
        partner = useStore(state => state.current_client, {store});

        mounted() {
            super.mounted();

            const partnerSuggestions = []
            _.each(this.props.pos.db.partner_by_id, partner_id => {
                partnerSuggestions.push({
                    search: this.props.pos.db._partner_search_string(partner_id),
                    label: partner_id.name,
                    data: {
                        partner: partner_id
                    },
                    dataset: {
                        'id': partner_id.id,
                    },
                    onclick: event => {
                        this.props.pos.get_order().set_client(partner_id);
                    },
                })
            })

            this.state.autoCompleteInput = new AutoCompleteInput({
                inputElement: this.el.querySelector('.client_selection__input'),
                suggestionList: partnerSuggestions,
                filters: {
                    'student': function (content) {
                        return content.data.partner.person_type === 'student';
                    },
                    'has_invoices': function (content) {
                        return content.data.partner.pos_wallet_has_invoice;
                    },
                    'has_unpaid_invoices': function (content) {
                        return content.data.partner.pos_wallet_has_unpaid_invoice;
                    },
                }
            });
        }

        toggleStudentFilter() {
            this.state.autoCompleteInput.toggleFilter('student');
        }

        btnLoadWalletPopup() {
            const walletList = this.props.pos.config.wallet_category_ids.map(wallet_id => this.props.pos.chrome.call('WalletService', 'getWalletById', wallet_id));

            this.props.pos.gui.show_popup('posPrLoadWallet', {
                title: _t('Load wallet'),
                wallets: walletList,
                body: _t('Testing wallet'),
            });
        }
    }

    // Payment
    class WalletPaymentCardCompoment extends Component {

        constructor(parent, props) {
            super(parent, props);
            console.log('Constructor WalletPaymentCardCompoment');

            const {walletCategory} = props || {walletCategory: {}};

            this.state = useState({
                id: walletCategory.id,
                name: walletCategory.name,
                payment_amount: 0,
                categoryList: [],
            });

            this.walletCategory = useState(walletCategory);
        }

        walletInput = useRef("walletInput");
        dispatch = useDispatch(store);
        todos = useStore(state => state.todos, {store});
        client_wallet_balances = useStore(state => state.client_wallet_balances, {store});

        get matchCategory() {
            const orderCategoryIds = _.chain(this.state.categoryList).map(categ => {
                const categoryIds = this.getCategParents(categ);
                return categoryIds;
            }).reduce((memo, newArray) => memo.concat(newArray), []).value();
            return this.props.walletCategory.is_default_wallet || (orderCategoryIds.indexOf(this.props.walletCategory.category.id) !== -1);
        }

        getCategParents(categ) {
            return (categ.parent ? this.getCategParents(categ.parent) : []).concat([categ.id])
        }

        patched(snapshot) {
            const res = super.patched(snapshot)
            if (!this.matchCategory) {
                const paymentAmount = 0;
                this.state.payment_amount = paymentAmount;
                this.trigger('pos-wallet-card-input', {
                    paymentAmount,
                    walletCategory: this.walletCategory,
                });
            }
            return res
        }

        triggerInputAction(event) {
            const decimals = ((window.posmodel && window.posmodel.currency) ? window.posmodel.currency.decimals : 2) || 2;
            let paymentAmount = verifyInputNumber(this.walletInput.el, decimals);

            if (this.client_wallet_balances[this.state.id] - paymentAmount < -Math.abs(this.props.walletCategory.credit_limit)) {
                paymentAmount = this.client_wallet_balances[this.state.id] - Math.abs(this.props.walletCategory.credit_limit);
            }
            if (this.matchCategory) {
                this.state.payment_amount = paymentAmount;
                this.walletInput.el.value = paymentAmount
                this.trigger('pos-wallet-card-input', {
                    paymentAmount,
                    walletCategory: this.walletCategory,
                });
            } else {
                this.state.payment_amount = 0;
            }
        }
    }

    class PosWalletPaymentSTComponent extends Component {
        static props = ['pos', 'height', 'categoryList'];

        spaceTree = useRef('spaceTree');

        constructor(parent, props) {
            super(...arguments);

            const posWalletsIds = this.props.pos.config.wallet_category_ids;
            const wallets = [];
            _.each(posWalletsIds, walletId => {
                const walletCategory = this.props.pos.chrome.call('WalletService', 'getWalletById', walletId);
                wallets.push(walletCategory);
            });

            this.state = useState({
                wallets,
            });
        }

        willUpdateProps(nextProps) {
            const result = super.willUpdateProps(nextProps);

            if (Object.hasOwnProperty.call(nextProps, 'categoryList')) {
                const categoryList = nextProps.categoryList;
                for (const children in this.__owl__.children) {
                    if (Object.hasOwnProperty.call(this.__owl__.children, children)) {
                        this.__owl__.children[children].state.categoryList = categoryList;
                    }
                }
            }

            console.log(result)
            return result;
        }

        getOrderWalletPayment() {

            const walletPaymentAmounts = {};

            _.each(this.wallet_cards, wallet_card => {
                if (wallet_card.state.payment_amount) {
                    walletPaymentAmounts[parseInt(wallet_card.state.id)] = wallet_card.state.payment_amount;
                }
            })

            return walletPaymentAmounts;
        }

        mounted() {
            super.mounted();

            if (this.wallet_cards) {
                _.each(this.wallet_cards, wallet_card => wallet_card.unmount());
            }

            this.wallet_cards = [];

            if (this.props.height) {
                const posWalletPaymentSpaceTree = this.spaceTree.el;
                posWalletPaymentSpaceTree.style.height = (Number(this.props.height) || 0) + 'px';
            }

            this._generateSpaceTree();
            this._refreshSpaceTree()
        }

        payWithWallet() {
            this.trigger('pos-wallet-make-payment', this.getOrderWalletPayment());
        }

        /**
         * @param {Number} height
         */
        resizeSpaceTreeHeight(height) {
            this.st.canvas.resize(this.st.canvas.element.offsetWidth, height || 0)
        }

        /**
         * @param walletId
         * @private
         */
        _getWalletCategorySpaceTreeJSON(walletId) {

            const walletCategory = this.props.pos.chrome.call('WalletService', 'getWalletById', walletId);

            const walletCategoryJSON = {
                id: `node-wallet-${this.__owl__.id}-${walletId}`,
                name: walletCategory.name,
                data: {
                    id: walletId
                }
            };


            if (walletCategory.child_wallet_ids) {
                walletCategoryJSON.children = [];
                _.each(walletCategory.child_wallet_ids, childWalletId => {
                    if (_.find(this.props.pos.config.wallet_category_ids, id => id === childWalletId)) {
                        walletCategoryJSON.children.push(this._getWalletCategorySpaceTreeJSON(childWalletId))
                    }
                });
            }

            return walletCategoryJSON;
        }

        /**
         * @private
         */
        _generateSpaceTree() {
            const posWalletPaymentSpaceTree = this.spaceTree.el;
            $(posWalletPaymentSpaceTree).empty();

            const level_count = Math.max.apply(Math, this.state.wallets.map(wallet => wallet.parent_wallet_count)) + 1

            const nodeWidth = 250;
            const levelDistance = 50;
            const offsetX = ((level_count * nodeWidth)) / 2;

            this.st = new $jit.ST({
                //id of viz container element
                injectInto: posWalletPaymentSpaceTree,
                //set duration for the animation
                duration: 0,
                ////set distance between node and its children
                levelDistance: levelDistance,

                // To center the whole thing
                offsetX: offsetX,
                offsetY: this.header_heigth / 2,

                constrained: false,
                //set node and edge styles
                //set overridable=true for styling individual
                //nodes or edges
                Node: {
                    width: nodeWidth,
                    height: 140,
                    type: 'rectangle',
                    overridable: true
                },

                Edge: {
                    type: 'line',
                    overridable: true
                },

                /**
                 * This method is called on DOM label creation.
                 * Use this method to add event handlers and styles to
                 * your node.
                 * @param {HTMLElement} label
                 * @param {Object} node
                 * @private
                 */
                onCreateLabel: (label, node) => {
                    label.id = node.id;
                    const walletCategory = this.props.pos.chrome.call('WalletService', 'getWalletById', node.data.id);
                    const walletPaymentCard = new WalletPaymentCardCompoment(this, {
                        walletCategory,
                        categoryList: this.props.categoryList
                    });

                    this.wallet_cards.push(walletPaymentCard);

                    walletPaymentCard.env.store = store;
                    walletPaymentCard.mount(label);
                },
            });
            //load json data
            this.st.loadJSON(this._getWalletsSpaceTreeJSON());
        }

        /**
         * @private
         */
        _getWalletsSpaceTreeJSON() {
            const defaultWallet = this.props.pos.chrome.call('WalletService', 'getDefaultWallet');
            return this._getWalletCategorySpaceTreeJSON(defaultWallet.id);
        }

        _refreshSpaceTree() {
            //compute node positions and layout
            this.st.compute();
            //optional: make a translation of the tree
            this.st.select(this.st.root);
        }
    }

    class PosWalletPaymentScreenComponent extends Component {

        static components = {PosWalletPaymentSTComponent};
        static props = ['pos'];

        wallet_cards = [];
        button_labels = {
            show: _t('Show'),
            hide: _t('Hide'),
        };
        height = 0;
        header_heigth = 150;
        state = useState({
            show: false,
            button_label: this.button_labels.show,
            categoryList: [],
        });

        payWithWallet(orderWalletPayments) {
            const order = this.props.pos.get_order();

            // We create and add the payment line
            _.each(orderWalletPayments.detail || {}, (paymentAmount, walletId) => {
                const paymentMethod = this.props.pos.db.payment_method_by_wallet_id[parseInt(walletId)];
                const newPaymentline = new Paymentline({}, {
                    order: order,
                    payment_method: paymentMethod,
                    pos: this.props.pos
                });
                newPaymentline.set_amount(paymentAmount);
                store.dispatch('substractWalletAmount', walletId, paymentAmount);

                newPaymentline.set_payment_status('done');
                newPaymentline.paid = true;
                newPaymentline.isWalletPayment = true;
                console.log('newPaymentline: ' + newPaymentline)
                order.paymentlines.add(newPaymentline)
            });

            // order.set_wallet_payments(orderWalletPayments);
            this.props.pos.gui.show_screen('payment');
        }

        /**
         * @override
         */
        mounted() {
            super.mounted();
            const spaceTreeHeight = document.querySelector('.product-list-scroller.touch-scrollable').offsetHeight
            _.each(this.__owl__.children, child => {
                child.resizeSpaceTreeHeight(spaceTreeHeight);
            });
        }

        /**
         *
         * @param {OwlEvent} event
         */
        toggleShow(event) {
            const forceState = event.detail;
            this.state.show = forceState !== undefined ? !!forceState : !this.state.show;
            this.state.button_label = this.state.show ? this.button_labels.hide : this.button_labels.show;

            if (this.state.show) {
                this.updateCategoryList();
                this.el.classList.remove('payment-wallet-dashboard--hidden');
            } else {
                this.state.categoryList = [];
                this.el.classList.add('payment-wallet-dashboard--hidden');
            }
        }

        updateCategoryList() {
            this.state.categoryList = _.map(this.props.pos.get_order().orderlines.models, ol => ol.product.categ);
        }
    }

    return {
        // Partner Screen
        WalletPaymentCardCompoment,
        PosWalletPartnerScreenComponent,

        // Payment Screen
        PosWalletPaymentSTComponent,
        PosWalletPaymentScreenComponent,
    }
});