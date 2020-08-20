odoo.define('pos_pr.tools', function (require) {

    function cast_to_float(value) {
        let casted_value = parseFloat(value);
        return isNaN(casted_value) ? 0 : casted_value;
    }

    function sum_object_properties(obj) {
        let sum = 0;
        for (let el in obj) {
            if (obj.hasOwnProperty(el)) {
                sum += cast_to_float(obj[el]);
            }
        }
        return sum;
    }

    function format_date(date) {
        const offset = date.getTimezoneOffset()
        let corrected_date = new Date(date.getTime() + (offset * 60 * 1000))
        return date.toISOString().split('T')[0]
    }

    return {
        cast_to_float: cast_to_float,
        sum_object_properties: sum_object_properties,
        format_date: format_date,
    }
});