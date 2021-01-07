odoo.define('pos_partner_panel.owl.store', require => {
    "use strict";

    const store = new owl.Store({
        state: {
            current_client: {},
        },
        actions: {
            setPartner({state}, newPartner) {
                state.current_client = newPartner;
            }
        }
    });
    store.on('update', null, () => console.log(store.state.current_client));
    return store;

});