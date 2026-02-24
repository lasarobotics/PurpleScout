$(document).ready(function () {


    var socket = io();

    // Tell the server that this scouter is ready
    //const username = prompt('Enter your name: ');
    //socket.emit('scouterReady', {name: username});

    const assign = document.getElementById('preMatch');
    const waiting = document.getElementById('waiting');
    const form = document.getElementById('scoutForm');
    const team_text = $('#waiting b span');

    var selectedTeam = null;

    function handleClick() {
        alert('Button was clicked!');
    }

    var teamID = $('#cookieTeamNum').text()

    // var myButtonElement = null

    if (teamID != null){
        console.log(teamID);
        var $btn = $('#' + teamID);
        $btn.trigger('click');
        console.log($btn);
    }
    // document.getElementById(teamID).buttonClick();
    
    // var myButtonElement = document.getElementById(teamID);
    // // myButtonElement.addEventListener('click', handleClick);
    // console.log(myButtonElement)
    // myButtonElement.click();

    async function getBatteryInfo() {
        try {
            const battery = await navigator.getBattery();
            const batteryInfo = {
                percent: battery.level * 100,
                plugged: battery.charging,
                chargingTime: battery.chargingTime,
                dischargingTime: battery.dischargingTime
            };
            console.log("Battery Info:", batteryInfo.percent, batteryInfo.plugged);
            percentage = batteryInfo.percent;
            pluggedIn = batteryInfo.plugged;

            return { percent: percentage, pluggedIn: pluggedIn };
        } catch (error) {
            return "error";

        }
    }

    // Call the function to get battery info


    // Team select handler
    $('button.teamSelect').click(function() {
        selectTeam(this.id); // call the same function
    });
        
    async function selectTeam(teamID) {
        //assign.style.display = 'none';
        //waiting.style.display = 'block';
        console.log("aaah");
        percentage = 0;
        pluggedIn = false;
        console.log(navigator.getBattery());
        // const battery = await navigator.getBattery();
        
        try {
            const battery = await navigator.getBattery();
            const batteryInfo = {
                percent: battery.level * 100,
                plugged: battery.charging,
                chargingTime: battery.chargingTime,
                dischargingTime: battery.dischargingTime
            };
            console.log("Battery Info:", batteryInfo.percent, batteryInfo.plugged);
            percentage = batteryInfo.percent;
            pluggedIn = batteryInfo.plugged;
        } catch (error) {
            return "error";

        }

        // emit scoutSelect event with the id of the button clicked
        if (this.id != 'deselect') {


            // deselect the current one, and select the new one
            socket.emit('scoutSelect', { type: selectedTeam, action: 'deselect' })
            socket.emit('scoutSelect', { type: this.id, scoutID: $('#scoutID').val(), action: 'select', batteryP: percentage, batteryPlug: pluggedIn });
            // show the waiting message
            waiting.style.display = 'block';
            team_text.text(this.id);
            selectedTeam = this.id;
            console.log(selectedTeam);

            if (this.id.includes('red')) {
                $('.color-fade').css('background-color', '#c93434');
                $('tbody tr:last-of-type').css('border-bottom-color', '#c93434');
            } else {
                $('.color-fade').css('background-color', '#333399');
                $('tbody tr:last-of-type').css('border-bottom-color', '#333399');
            }
        } else {
            // deselect: reset all values to default
            team_text.text('None');
            $('.color-fade').css('background-color', '#663399');
            $('tbody tr:last-of-type').css('border-bottom-color', '#663399');
            socket.emit('scoutSelect', { type: selectedTeam, action: 'deselect' });
        }
    };

    // When another scouter clicks a button, disable it
    socket.on('scoutSelect', function (data) {
        console.log(data);
        if (data.action == 'select') {
            $('#' + data.type).prop('disabled', true);
        } else {
            $('#' + data.type).prop('disabled', false);
        }
    });


    // When the mega scout gives the go ahead, start the match
    socket.on('scoutAssign', function (data) {
        console.log('Scouter ' + selectedTeam + ' is assigned to team ' + data[selectedTeam]);
        alert("The mega scout has started Match #" + data.matchNum + "! You are scouting " + selectedTeam + " and have been assigned to team " + data[selectedTeam] + ".");

        // update ui
        $('#teamNum').val(data[selectedTeam]);
        $('#matchNum').val(data.matchNum);

        // scroll down to form
        document.querySelector('div.horizontalBlock').scrollIntoView({
            behavior: 'smooth',
            block: 'center',
        });
    });

    // Tooltip below 'Broken' field
    tippy('#fumbleTr', {
        content: 'Did the robot drop a piece while intaking, carrying, or attempting to score? Explain in comments.',
        placement: 'left',
        animation: 'fade',
    });
    tippy('#foulTr', {
        content: 'Did the ref point at your robot and wave a flag? Explain in comments.',
        placement: 'left',
    });
    tippy('#brokenTr', {
        content: 'Check if there was a <b>critical failure</b> (ex. broken part, frozen, or stuck piece) that rendered the robot basically useless. Explain in comments.',
        placement: 'left',
        allowHTML: true,
    });
    tippy('#mobilityTr', {
        content: 'Are the robot\'s bumpers completely across the starting line at the end of AUTO?',
        placement: 'top',
    });
    tippy('#defenseTr', {
        content: 'Did the robot cross over to the opposite side of the field and actively play contact defense? Explain in comments.',
        placement: 'top',
    });
    tippy('#info', {
        // content: document.getElementById('infoTooltip').innerHTML,
        placement: 'top',
        allowHTML: true,
        trigger: 'click',
        maxWidth: 'none',
    });


    /*
    const keysPressed = {};
    // Keyboard shortcuts
    $(document).on('keydown', function(e) {
        // Skip if the focus is in a text input, textarea, or contenteditable element
        if ($(e.target).is('input, textarea, [contenteditable="true"]')) {
            return;
        }
        console.log(e.which);
    
        if (!keysPressed[e.which]) {
            keysPressed[e.which] = true;
            switch (e.key) {
                case '4':
                    $('#coralL4Inc').click();
                    break;
                case '3':
                    $('#coralL3Inc').click();
                    break;
                case '2':
                    $('#coralL2Inc').click();
                    break;
                case '1':
                    $('#coralL1Inc').click();
                    break;
            }
        }
    });
    
    $(document).on('keyup', function (e) {
        keysPressed[e.which] = false;
    });
    */

});