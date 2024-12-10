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
            $('#alliance').val("red");
            $('.alliance-color').text("Red");
        } else if (this.id === "blueSuper") {
            team_text.text("BLUE");
            $('.color-fade').css('background-color', '#333399');  
            $('#alliance').val("blue"); 
            $('.alliance-color').text("Blue");
        }
        //team_text.text(this.id);
        selectedTeam = this.id;
        console.log(selectedTeam)

    } else {
        // deselect: reset all values to default
        team_text.text('None');
        $('.color-fade').css('background-color', '#663399');
        socket.emit('scoutSelect', {type: selectedTeam, action: 'deselect'});
        $('#alliance').val("none");
        $('.alliance-color').text("Robot");
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
    //console.log('Scouter ' + selectedTeam + ' is assigned to team ' + data[selectedTeam]);
    alert("The super scout has started match #" + data.matchNum + "! Collect data about your alliance.");

    // update ui
    //$('#teamNum').val(data[selectedTeam]);
    $('#matchNum').val(data.matchNum);
    console.log(data);

    // set the table headers to update correct team numbers
    if (selectedTeam === "redSuper") {
        $('#robot1-num').text(' (' + data['red1'].toString() + ')');
        $('#robot2-num').text(' (' + data.red2.toString() + ')');
        $('#robot3-num').text(' (' + data.red3.toString() + ')');
    } else if (selectedTeam === "blueSuper") {
        $('#robot1-num').text(' (' + data.blue1.toString() + ')');
        $('#robot2-num').text(' (' + data.blue2.toString() + ')');
        $('#robot3-num').text(' (' + data.blue3.toString() + ')');
    }

});