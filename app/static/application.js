
// https://stackoverflow.com/questions/23451611/is-there-anyway-to-have-a-textarea-autofit-height-based-on-the-content-at-page
function autofit_textarea_height() {
    var addon;
    var textarea = document.getElementById("ti_instructions");

    if (textarea.clientHeight < textarea.scrollHeight) {
        if (screen.width < 601) { // w3-hide-small
            addon = 10
        } else if (screen.width < 992) { // w3-hide-medium
            addon = 7
        } else { // w3-hide-large
            addon = 5
        }

        textarea.style.height = textarea.scrollHeight + addon + "px";
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
        edit.style.display = 'block';
        highlight.style.display = 'none';
    } else {
        edit.style.display = 'none';
        highlight.style.display = 'block';
    }
}

function toggle_highlight_edit() {
    var highlighted = document.getElementById("highlighted");
    var edit = document.getElementById("edit");
    var highlight = document.getElementById("highlight");
    var highlighted = document.getElementById("highlighted");
    var ti_instructions = document.getElementById("ti_instructions");
    var value;

    if (highlighted.style.display === "none") {
        edit.style.display = "inline";
        highlight.style.display = "none";

        ti_instructions.style.display = "none";
        // Keep in sync with filter.py/nl2br_and_nbsp()
        value = ti_instructions.value.replace(/\n/g, "<br>").replace(/ /g, "&nbsp;")
        highlighted.innerHTML = w3CodeColorize(value, "python");
        highlighted.style.display = "block";

        set_cookie("instructions_display", "highlighted")
    } else {
        edit.style.display = "none";
        highlight.style.display = "inline";

        ti_instructions.style.display = "block";
        highlighted.style.display = "none";
        autofit_textarea_height();

        set_cookie("instructions_display", "edit")
    }
}

function toggle_show_hide(name) {
    var x = document.getElementById(name);

    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}
