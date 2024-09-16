// Page load tasks, mostly assigning event handlers and names that Copilot did for me, I'm lazy :P

function load() {
    // 1. Find all the input elements that are not radio buttons and set their name field to their id field
    var inputs = document.getElementsByTagName("input");
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].type != "radio") {
            inputs[i].name = inputs[i].id;
        }
    }


    // 2. Find all the buttons that have a class of "addButton" and add an onclick event that calls the increase function
    var incButtons = document.getElementsByClassName("addButton");
    for (var i = 0; i < incButtons.length; i++) {
        incButtons[i].onclick = function () {
            // Get the previous sibling element in the DOM tree
            var sibling = this.previousElementSibling;
            // Call the increase function with the button's id
            increase(sibling.id);

        }
    }

    // 3. Do the same for decrease buttons
    var decButtons = document.getElementsByClassName("subtractButton");
    for (var i = 0; i < decButtons.length; i++) {
        decButtons[i].onclick = function () {
            // Get the next sibling element in the DOM tree
            var sibling = this.nextElementSibling;
            // Call the decrease function with the button's id
            decrease(sibling.id);
        }
    }
}

// Run the load function when the page loads fully
window.onload = load;


// generalized inc and dec functions
function increase(id) {
    curVal = document.getElementById(id).value;
    curVal++;
    document.getElementById(id).value = curVal;
}

function decrease(id) {
    curVal = document.getElementById(id).value;
    if (curVal == 0) {
        curVal = 0;
    } else {
        curVal--;
    }
    document.getElementById(id).value = curVal;
}


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

