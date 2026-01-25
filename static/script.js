console.log("[PurpleScout] script.js is loading...");

// 1. Core Logic Functions (Global Scope)
/**
 * Robustly updates an input value
 * @param {HTMLInputElement|string} target - The input element or its ID
 * @param {number} amount - Amount to add (can be negative)
 */
function updateValue(target, amount) {
    var el = (typeof target === 'string') ? document.getElementById(target) : target;

    if (!el) {
        console.error('[Counter] Update failed: Target element not found', target);
        return;
    }

    var curVal = parseInt(el.value);
    if (isNaN(curVal)) curVal = 0;

    var newVal = curVal + amount;
    if (newVal < 0) newVal = 0; // Prevent negative scores

    el.value = newVal;

    // Trigger 'change' event for reactive systems (e.g. Flask/React/etc)
    el.dispatchEvent(new Event('change', { bubbles: true }));

    console.log(`[Counter] Updated ${el.id || el.name} by ${amount}. Old: ${curVal}, New: ${newVal}`);
}

// Global wrappers for older styles
function increase(id, amount) { updateValue(id, amount || 1); }
function decrease(id) { updateValue(id, -1); }

// 2. Event Delegation (Global Scope - Runs immediately)
// This listener picks up any click on the page and checks if it's one of our buttons
document.addEventListener('click', function (event) {
    // Navigate up from the click target to find our button
    var button = event.target.closest('button');
    if (!button) return;

    // Check if this button is inside one of our counter groups
    var container = button.closest('.addsubInput');
    if (!container) return;

    // We found a counter button! Now find the input it belongs to
    var input = container.querySelector('input');
    if (!input) {
        console.warn('[Counter] Found button group but no input field inside.', container);
        return;
    }

    // Determine the action based on class names
    if (button.classList.contains('addButton')) {
        updateValue(input, 1);
    } else if (button.classList.contains('add5Button')) {
        updateValue(input, 5);
    } else if (button.classList.contains('add10Button')) {
        updateValue(input, 10);
    } else if (button.classList.contains('subtractButton')) {
        updateValue(input, -1);
    } else {
        // Fallback for buttons that might only have text content or generic classes
        if (button.innerText.includes('+5')) updateValue(input, 5);
        else if (button.innerText.includes('+10')) updateValue(input, 10);
        else if (button.innerText.includes('+')) updateValue(input, 1);
        else if (button.innerText.includes('-')) updateValue(input, -1);
    }
});

// 3. Initialization Logic (Wait for DOM)
document.addEventListener('DOMContentLoaded', function () {
    console.log("[PurpleScout] DOM fully loaded, initializing inputs...");

    // Ensure all inputs have a 'name' attribute matching their 'id' (Crucial for Flask-WTF)
    var inputs = document.getElementsByTagName("input");
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].type !== "radio" && inputs[i].id) {
            inputs[i].name = inputs[i].id;
        }
    }
});


// Download the csv file
function download_csv_file(event) {
    bool = true;
    var teamNum = document.getElementById("teamNum").value;
    var autoConeLow = document.getElementById("auto-low-cones").value;
    var autoCubeLow = document.getElementById("auto-low-cubes").value;
    var autoConeMid = document.getElementById("auto-mid-cones").value;
    var autoCubeMid = document.getElementById("auto-mid-cubes").value;
    var autoConeHigh = document.getElementById("auto-high-cones").value;
    var autoCubeHigh = document.getElementById("auto-high-cubes").value;
    var teleConeLow = document.getElementById("teleop-low-cones").value;
    var teleCubeLow = document.getElementById("teleop-low-cubes").value;
    var teleConeMid = document.getElementById("teleop-mid-cones").value;
    var teleCubeMid = document.getElementById("teleop-mid-cubes").value;
    var teleConeHigh = document.getElementById("teleop-high-cones").value;
    var teleCubeHigh = document.getElementById("teleop-high-cubes").value;

    var defense1 = document.getElementById("def1");
    var defense2 = document.getElementById("def2");
    var defense3 = document.getElementById("def3");
    var defense4 = document.getElementById("def4");
    var def = 0;
    var substation1 = document.getElementById("sub1");
    var substation2 = document.getElementById("sub2");
    var substation3 = document.getElementById("sub3");
    var sub = 0;
    var dropped = document.getElementById("dropped-pieces").value;
    var addInfo = document.getElementById("info").value;

    if (defense1.checked) {
        def = 0;
    }
    else if (defense2.checked) {
        def = 1;
    }
    else if (defense3.checked) {
        def = 2;
    }
    else if (defense4.checked) {
        def = 3;
    }
    else {
        def = -1

        alert("You have not indicated how the defense was performed! Please take a look at this before submitting. :)")
        event.preventDefault();
        bool = false
        return false;
    }

    if (substation1.checked) {
        sub = 0;
    } else if (substation2.checked) {
        sub = 1;
    } else if (substation3.checked) {
        sub = 2
    } else {
        sub = -1;
        alert("You have not indicated which substation was primarily used! Please take a look at this before submitting. :)")
        event.preventDefault();
        bool = false;
        return false;
    }
    console.log(bool)
    if (bool) {
        var data = [];
        data.push(parseInt(teamNum));
        data.push(parseInt(autoConeLow));
        data.push(parseInt(autoConeMid));
        data.push(parseInt(autoConeHigh));
        data.push(parseInt(autoCubeLow));
        data.push(parseInt(autoCubeMid));
        data.push(parseInt(autoCubeHigh));
        data.push(parseInt(teleConeLow));
        data.push(parseInt(teleConeMid));
        data.push(parseInt(teleConeHigh));
        data.push(parseInt(teleCubeLow));
        data.push(parseInt(teleCubeMid));
        data.push(parseInt(teleCubeHigh));
        data.push(parseInt(def));
        data.push(parseInt(sub));
        data.push(parseInt(dropped));
        data.push(addInfo);
        var data_string = JSON.stringify(data);


        var newData = data_string.substring(1, data_string.length - 1);


        // Download the file
        var file = new Blob([newData], { type: "text" });
        var anchor = document.createElement("a");
        anchor.href = URL.createObjectURL(file);
        // // let count = nameCount = sessionStorage.getItem("count");
        // // let string = name + "-" + nameCount + ".txt";
        let string = "form.txt"
        anchor.download = string;
        anchor.click();

        // let numCount = parseInt(sessionStorage.getItem("count"));
        // numCount++;
        // sessionStorage.setItem("count", numCount);
        //location.reload();
        return true; // we're ok to submit the form now!
    } else {
        event.preventDefault();
    }

}















// unused repetitive code _________________________________________________________________________________________________________
/*


function inc() {
    curVal = document.getElementById('number').value;
    curVal++
    document.getElementById("number").value = curVal;
}

function dec() {
    curVal = document.getElementById('number').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("number").value = curVal;
}

function incb() {
    curVal = document.getElementById('numberb').value;
    curVal++
    document.getElementById("numberb").value = curVal;
}

function decb() {
    curVal = document.getElementById('numberb').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("numberb").value = curVal;
}

function incTwo() {
    curVal = document.getElementById('numberB').value;
    curVal++
    document.getElementById("numberB").value = curVal;
}

function decTwo() {
    curVal = document.getElementById('numberB').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("numberB").value = curVal;
}

function incTwob() {
    curVal = document.getElementById('numberBb').value;
    curVal++
    document.getElementById("numberBb").value = curVal;
}

function decTwob() {
    curVal = document.getElementById('numberBb').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("numberBb").value = curVal;
}
// _________________________________________________________________________________________________________



function inc2() {
    curVal = document.getElementById('number2').value;
    curVal++
    document.getElementById("number2").value = curVal;
}

function dec2() {
    curVal = document.getElementById('number2').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("number2").value = curVal;
}

function inc2b() {
    curVal = document.getElementById('number2b').value;
    curVal++
    document.getElementById("number2b").value = curVal;
}

function dec2b() {
    curVal = document.getElementById('number2b').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("number2b").value = curVal;
}

function incTwo2() {
    curVal = document.getElementById('numberB2').value;
    curVal++
    document.getElementById("numberB2").value = curVal;
}

function decTwo2() {
    curVal = document.getElementById('numberB2').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("numberB2").value = curVal;
}

function incTwo2b() {
    curVal = document.getElementById('numberB2b').value;
    curVal++
    document.getElementById("numberB2b").value = curVal;
}

function decTwo2b() {
    curVal = document.getElementById('numberB2b').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("numberB2b").value = curVal;
}



// _________________________________________________________________________________________________________




function inc3() {
    curVal = document.getElementById('number3').value;
    curVal++
    document.getElementById("number3").value = curVal;
}

function dec3() {
    curVal = document.getElementById('number3').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("number3").value = curVal;
}

function inc3b() {
    curVal = document.getElementById('number3b').value;
    curVal++
    document.getElementById("number3b").value = curVal;
}

function dec3b() {
    curVal = document.getElementById('number3b').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("number3b").value = curVal;
}


function incTwo3() {
    curVal = document.getElementById('numberB3').value;
    curVal++
    document.getElementById("numberB3").value = curVal;
}

function decTwo3() {
    curVal = document.getElementById('numberB3').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("numberB3").value = curVal;
}

function incTwo3b() {
    curVal = document.getElementById('numberB3b').value;
    curVal++
    document.getElementById("numberB3b").value = curVal;
}

function decTwo3b() {
    curVal = document.getElementById('numberB3b').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("numberB3b").value = curVal;
}




function incThree() {
    curVal = document.getElementById('numberC').value;
    curVal++
    document.getElementById("numberC").value = curVal;
}

function decThree() {
    curVal = document.getElementById('numberC').value;
    if (curVal == 0) {
        curVal = 0
    }
    else {
        curVal--
    }
    document.getElementById("numberC").value = curVal;
}


*/
