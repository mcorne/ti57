
// https://stackoverflow.com/questions/23451611/is-there-anyway-to-have-a-textarea-autofit-height-based-on-the-content-at-page
function autofit_textarea_height(name) {
    var textarea = document.getElementById(name);

    if (textarea.clientHeight < textarea.scrollHeight) {
        textarea.style.height = textarea.scrollHeight + 5 + "px";
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
