
// https://stackoverflow.com/questions/23451611/is-there-anyway-to-have-a-textarea-autofit-height-based-on-the-content-at-page
function autofit_instructions_height() {
    var padding;
    var ti_instructions = document.getElementById("ti_instructions");

    if (ti_instructions.clientHeight < ti_instructions.scrollHeight) {
        if (screen.width < 601) { // w3-hide-small
            padding = 10
        } else if (screen.width < 992) { // w3-hide-medium
            padding = 7
        } else { // w3-hide-large
            padding = 5
        }

        ti_instructions.style.height = (ti_instructions.scrollHeight + padding) + "px";
    }
}

function close_sidebar() {
    document.getElementById("overlay").style.display = "none";
    document.getElementById("sidebar").style.display = "none";
}

function dropdown_click(name) {
    var x = document.getElementById(name);

    if (x.className.indexOf("w3-show") == -1) {
        x.className += " w3-show";
        x.previousElementSibling.className += " w3-indigo";
    } else {
        x.className = x.className.replace(" w3-show", "");
        x.previousElementSibling.className = x.previousElementSibling.className.replace(" w3-indigo", "");
    }
}

function erase_instructions() {
    var ti_instructions = document.getElementById("ti_instructions");

    if (ti_instructions.style.display == "none") {
        toggle_x_y('edit', 'highlight', 'ti_instructions', 'highlighted');
        set_cookie("instructions_display", "edit")
    }

    ti_instructions.value = "";

    if (screen.width < 601) { // w3-hide-small
        ratio = 0.4
    } else if (screen.width < 992) { // w3-hide-medium
        ratio = 0.3
    } else { // w3-hide-large
        ratio = 0.2
    }

    ti_instructions.style.height = (screen.width * ratio) + "px";
}

// https://www.w3schools.com/js/js_cookies.asp
function get_cookie(name) {
    var name = name + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function open_sidebar() {
    document.getElementById("overlay").style.display = "block";
    document.getElementById("sidebar").style.display = "block";
}

function save_input_data() {
    var index = 0;
    var input_data = document.getElementById("input_data");
    var replacement;
    var ti_instructions = document.getElementById("ti_instructions");
    var values;

    document.getElementById("input_data_message").style.display = "none";

    values = input_data.innerText.trim();
    if (!values) {
        input_data.innerText = 0; // must enter something to be able to edit
        return true;
    }

    values = values.replace(/\s+/g, " ");
    values = values.split(" ");
    if (!validate_input_data(values)) {
        return false;
    }

    ti_instructions.value = ti_instructions.value.replace(/^( *[\d.e-]+(?=[ \n\r]))/igm, function (match, p1) {
        if (typeof values[index] == "undefined") {
            // There is nothing to replace with, pass the match
            replacement = p1;
        } else {
            // Replace the match with the register value with same index
            // Change scientific notation "e" to "ee", leave "ee" unchanged
            replacement = values[index].replace(/(e)+/i, "$1$1");
        }
        index++;
        return replacement;
    });

    if (ti_instructions.style.display == "none") {
        document.getElementById("highlighted").innerHTML = w3CodeColorize(ti_instructions.value, "tiinstruction");
    }

    return true;
}

// https://www.w3schools.com/js/js_cookies.asp
function set_cookie(name, value, exdays = 30) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
}

function set_highlight_edit() {
    var edit = document.getElementById("edit");
    var highlight = document.getElementById("highlight");

    if (get_cookie('instructions_display') == 'highlighted') {
        edit.style.display = 'inline-block';
        highlight.style.display = 'none';
    } else {
        edit.style.display = 'none';
        highlight.style.display = 'inline-block';
    }
}

// https://www.w3schools.com/howto/howto_js_trigger_button_enter.asp
function submit_on_enter_key(event) {
    if (event.keyCode === 13) {
        // This is the enter key, cancel the default action, submit the form
        if (event.preventDefault) {
            event.preventDefault();
        }
        if (save_input_data()) {
            document.getElementById('program').submit();
        }
    }
}

function toggle_highlight_edit() {
    var highlighted = document.getElementById("highlighted");
    var ti_instructions = document.getElementById("ti_instructions");
    var value;

    toggle_x_y('edit', 'highlight', 'ti_instructions', 'highlighted');

    if (highlighted.style.display == "none") {
        autofit_instructions_height();
        set_cookie("instructions_display", "edit")
    } else {
        highlighted.innerHTML = w3CodeColorize(ti_instructions.value, "tiinstruction");
        set_cookie("instructions_display", "highlighted")
    }
}

function toggle_x_y(button_x_id, button_y_id, target_x_id, target_y_id = null) {
    var button_x = document.getElementById(button_x_id);
    var button_y = document.getElementById(button_y_id);
    var target_x = document.getElementById(target_x_id);
    if (target_y_id) {
        var target_y = document.getElementById(target_y_id);
    }

    if (button_x.style.display == "none") {
        button_x.style.display = "inline-block";
        button_y.style.display = "none";
        target_x.style.display = "none";
        if (target_y_id) {
            target_y.style.display = target_y instanceof HTMLTableElement ? "table" : "block";
        }
    } else {
        button_x.style.display = "none";
        button_y.style.display = "inline-block";
        target_x.style.display = "block";
        if (target_y_id) {
            target_y.style.display = "none";
        }
    }
}

function validate_input_data(values) {
    for (value of values) {
        if (isNaN(value.replace(/ee/i, "e"))) { // Change scientific notation "ee" to "e"
            var message = document.getElementById("input_data_message");
            message.innerText = "Invalid Number: " + value;
            message.style.display = "block";
            return false;
        }
    }

    return true;
}
