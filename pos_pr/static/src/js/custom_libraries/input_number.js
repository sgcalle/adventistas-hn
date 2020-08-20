function NumberInput(element, opts) {
    if (!opts) {
        opts = {}
    }

    let default_opts = {
        "decimal_limit": opts.decimal_limit || 0
    }

    if (element.tagName === 'INPUT') {

        element.onkeydown = event => {
            return event.key.match("(\\d|\\.|,|Arrow|Backspace|Delete|Tab)") !== null;
        };

        element.oninput = event => {

            let element_type = element.type;
            element.type = "text";

            let inputValue = parseFloat(element.value)
            let selection_position_start = element.selectionStart;
            let selection_position_end = element.selectionEnd;

            let inputDecimalPart = (inputValue % 1).toFixed(default_opts.decimal_limit).replace("0\.", "");
            element.value = Math.trunc(inputValue) + "." + inputDecimalPart;

            element.type = element_type;
            element.setSelectionRange(selection_position_start, selection_position_end);
        };
    }

    if (!element.value.match("^\\d+\\.?\\d+$")) {
        element.value = 0;
    }
    element.dispatchEvent(new Event("input"));


}