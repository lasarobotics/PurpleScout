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
        if (this.id === "redSuper") {
            team_text.text("RED");
            $('.color-fade').css('background-color', '#c93434');
        } else if (this.id === "blueSuper") {
            team_text.text("BLUE");
            $('.color-fade').css('background-color', '#333399');   
        }
        //team_text.text(this.id);
        selectedTeam = this.id;
        console.log(selectedTeam)

    } else {
        // deselect: hide the waiting message
        team_text.text('None');
        $('.color-fade').css('background-color', '#663399');
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
    alert("The super scout has started match #" + data.matchNum + "! Collect data about your alliance.");

    // update ui
    //$('#teamNum').val(data[selectedTeam]);
    $('#matchNum').val(data.matchNum);
});