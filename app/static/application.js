
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

function open_sidebar() {
    document.getElementById("overlay").style.display = "block";
    document.getElementById("sidebar").style.display = "block";
}
