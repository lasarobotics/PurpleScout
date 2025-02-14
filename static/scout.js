var socket = io();

// Tell the server that this scouter is ready
//const username = prompt('Enter your name: ');
//socket.emit('scouterReady', {name: username});

const assign = document.getElementById('preMatch');
const waiting = document.getElementById('waiting');
const form = document.getElementById('scoutForm');
const team_text = $('#waiting b span');

var selectedTeam = null;
// Team select handler
$('button.teamSelect').click(function() {
    //assign.style.display = 'none';
    //waiting.style.display = 'block';
    
    // emit scoutSelect event with the id of the button clicked
    if (this.id != 'deselect') {

        // deselect the current one, and select the new one
        socket.emit('scoutSelect', {type: selectedTeam, action: 'deselect'})
        socket.emit('scoutSelect', {type: this.id, scoutID: $('#scoutID').val(), action: 'select'});
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
        socket.emit('scoutSelect', {type: selectedTeam, action: 'deselect'});
    }
});

// When another scouter clicks a button, disable it
socket.on('scoutSelect', function(data) {
    console.log(data);
    if (data.action == 'select') {
        $('#' + data.type).prop('disabled', true);
    } else {
        $('#' + data.type).prop('disabled', false);
    }
});


// When the super scout gives the go ahead, start the match
socket.on('scoutAssign', function(data) {
    console.log('Scouter ' + selectedTeam + ' is assigned to team ' + data[selectedTeam]);
    alert("The super scout has started match #" + data.matchNum + "! You are scouting " + selectedTeam + " and have been assigned to team #" + data[selectedTeam] + ".");

    // update ui
    $('#teamNum').val(data[selectedTeam]);
    $('#matchNum').val(data.matchNum);

    // scroll down to form
    $('div.horizontalBlock')[0].scrollIntoView({
        behavior: 'smooth',
        block: 'center',
    });
});

// Tooltip below 'Broken' field
tippy('#phumbleTr', {
    content: 'Did the robot drop a piece while carrying or attempting to score? Explain in comments.',
    placement: 'left',
    animation: 'fade',
});
tippy('#foulTr', {
    content: 'Did the ref point at your robot and wave a flag? Explain in comments.',
    placement: 'left',
});
tippy('#brokenTr', {
    content: 'Did the robot break or freeze at any time? Explain in comments.',
    placement: 'left',
});
tippy('#defenseTr', {
    content: 'Did the robot cross over to the opposite side of the field and actively play contact defense? Explain in comments.',
    placement: 'top',
});
tippy('#info', {
    content: document.getElementById('infoTooltip').innerHTML,
    placement: 'top',
    allowHTML: true,
    trigger: 'click',
    maxWidth: 'none',
});