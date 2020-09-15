odoo.define('pos_pr.reports.append_templates_to_report', function (require) {

    const core = require('web.core');
    const widget = require('web.Widget');
    const QWeb = core.qweb;

    QWeb.add_template('/pos_pr/static/src/xml/screens/invoice_payment_receipt.xml', () => {

        const tJcallTemplates = document.querySelectorAll('[ot-jcall]');

        for (const tJCall of tJcallTemplates) {
            const templateName = tJCall.attributes['ot-jcall'].value;
            const templateHtml = QWeb.render(templateName);
            tJCall.innerHTML = templateHtml;
            console.log(templateHtml);
        }
    });



});
