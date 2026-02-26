$(document).ready(function () {


    var socket = io();

    const assign = document.getElementById('preMatch');
    const waiting = document.getElementById('waiting');
    const form = document.getElementById('scoutForm');
    const team_text = $('#waiting b span');

    var selectedTeam = null;

    var teamID = $('#cookieTeamNum').text().trim();
    console.log("Team ID from cookie:", teamID);
    if (teamID != 'None' && teamID != "") {
        selectedTeamProcess(teamID);
    } else {
        console.log("No team ID cookie found, starting with no team selected.");
        team_text.text('None');
        $('.color-fade').css('background-color', '#663399');
        $('tbody tr:last-of-type').css('border-bottom-color', '#663399');
        socket.emit('scoutSelect', { type: selectedTeam, action: 'deselect' });
    }


    // Team select handler
    $('button.teamSelect').click(function () {
        selectedTeamProcess(this.id)
    });

    async function selectedTeamProcess(teamID) {

        if (!teamID) return;

        percentage = 0;
        pluggedIn = false;
        console.log(navigator.getBattery());
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
        if (teamID != 'deselect') {

            // deselect the current one, and select the new one
            socket.emit('scoutSelect', { type: selectedTeam, action: 'deselect' })
            socket.emit('scoutSelect', { type: teamID, scoutID: $('#scoutID').val(), action: 'select', batteryP: percentage, batteryPlug: pluggedIn });
            // show the waiting message
            waiting.style.display = 'block';
            team_text.text(teamID);
            selectedTeam = teamID;
            console.log(selectedTeam);

            if (teamID.includes('red')) {
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
    }

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
        document.querySelector('div.rebuiltBlock').scrollIntoView({
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

});