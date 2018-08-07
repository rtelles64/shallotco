// Get the elements with class="column"
var elements = document.getElementsByClassName("column");

// Four images side by side
function four() {
	for (i = 0; i < elements.length; i++) {
        elements[i].style.msFlex = "25%";  // IE10
        elements[i].style.flex = "25%";
    }
}
