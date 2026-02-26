// Connect to the super scout namespace, for super scout specific events
var socket = io();

//socket.on('connect', function() {
    //socket.emit('my event', {data: 'I\'m connected!'});
//});

// super scouter knows status of each scout
// socket.on('scouterReady', function(data) {
//     console.log('Scouter ' + data.name + ' is ready!');

//     let team = prompt('Scouter ' + data.name + ' is ready! What team are they scouting?'); // this will be eventually be determined automatically
//     socket.emit('scoutAssign', {name: data.name, team: team});

// });

// ========== Side-by-Side DB Viewer with Real-Time Updates ==========

function renderTables(currentList, oldList) {
    // Clear existing tables
    $('#dbViewerContainer').html('');
    
    // Create container for two columns
    const container = $('<div style="display: flex; gap: 20px; margin-top: 20px;">');
    
    // Current DB table
    const currentTable = $('<div style="flex: 1;">');
    currentTable.append('<h3>Current Database (scouting_dat.db)</h3>');
    const currentTbl = $('<table class="tbl" style="width: 100%; font-size: 12px;"><thead><tr><th>Timestamp</th><th>Match</th><th>Team</th><th>Scout ID</th></tr></thead><tbody id="currentTableBody"></tbody></table>');
    currentTable.append(currentTbl);
    
    // Populate current table (use local tbody reference so we don't depend on DOM insertion order)
    const $currentTbody = currentTbl.find('tbody');
    if (!currentList || currentList.length === 0) {
        $currentTbody.append(`<tr><td colspan="4">No rows in current database</td></tr>`);
    } else {
        currentList.forEach(row => {
            $currentTbody.append(`<tr><td>${row.timestamp}</td><td>${row.matchNum}</td><td>${row.teamNum}</td><td>${row.scoutID}</td></tr>`);
        });
    }
    
    // Old DB table
    const oldTable = $('<div style="flex: 1;">');
    oldTable.append('<h3>Old Database (scouting_dat_old.db)</h3>');
    const oldTbl = $('<table class="tbl" style="width: 100%; font-size: 12px;"><thead><tr><th>Timestamp</th><th>Match</th><th>Team</th><th>Scout ID</th></tr></thead><tbody id="oldTableBody"></tbody></table>');
    oldTable.append(oldTbl);
    
    // Populate old table (use local tbody reference)
    const $oldTbody = oldTbl.find('tbody');
    if (!oldList || oldList.length === 0) {
        $oldTbody.append(`<tr><td colspan="4">No rows in old database</td></tr>`);
    } else {
        oldList.forEach(row => {
            $oldTbody.append(`<tr><td>${row.timestamp}</td><td>${row.matchNum}</td><td>${row.teamNum}</td><td>${row.scoutID}</td></tr>`);
        });
    }
    
    // Append both tables to container
    container.append(currentTable);
    container.append(oldTable);
    $('#dbViewerContainer').append(container);
}

async function fetchAndRender() {
    try {
        // Get the matchNum from the input field
        const matchNum = $('#matchNum').val();
        
        // Build the URL with optional matchNum parameter
        const currentUrl = matchNum ? `/api/mega/current?matchNum=${encodeURIComponent(matchNum)}` : '/api/mega/current';
        const oldUrl = matchNum ? `/api/mega/old?matchNum=${encodeURIComponent(matchNum)}` : '/api/mega/old';
        
        const [curRes, oldRes] = await Promise.all([
            fetch(currentUrl),
            fetch(oldUrl)
        ]);
        const curData = await curRes.json();
        const oldData = await oldRes.json();
        renderTables(curData, oldData);
    } catch (error) {
        console.error('Error fetching data:', error);
        $('#dbViewerContainer').html('<p style="color: red;">Error loading database data</p>');
    }
}

// Load tables on page load
$(document).ready(function() {
    fetchAndRender();
});

// disable the start match button until teams are fetched
$('#sendInfo').prop('disabled', true);

// Set current match when matchNum changes
$('#matchNum').on('input', function() {
    socket.emit('setCurrentMatch', {matchNum: $(this).val()});
    // Refresh the database tables with the new matchNum filter
    fetchAndRender();
});




// Fetch teams button handler
$('button#fetchTeams').click(function() {
    console.log('fetching teams');
    socket.emit('getTeams', {matchNum: $('#matchNum').val()});
    $('#red1teamNum').text('...');
    $('#red2teamNum').text('...');
    $('#red3teamNum').text('...');
    $('#blue1teamNum').text('...');
    $('#blue2teamNum').text('...');
    $('#blue3teamNum').text('...');
});
// ... receive the teams and display them
socket.on('sendTeams', function(data) {
    console.log(data);
    $('#red1teamNum').text(data.red1);
    $('#red2teamNum').text(data.red2);
    $('#red3teamNum').text(data.red3);
    $('#blue1teamNum').text(data.blue1);
    $('#blue2teamNum').text(data.blue2);
    $('#blue3teamNum').text(data.blue3);

    // enable the start button if there is no error
    if (data.red1 != 'error') {
        $('#sendInfo').prop('disabled', false);
    } else {
        $('#sendInfo').prop('disabled', true);
    }
});

// receive status updates from scouts
socket.on('scoutSelect', function(data) {
    console.log(data);
    pluggedIn=""
    if (data.batteryPlug){
        pluggedIn="🔌"
    } else if (!(data.batteryPlug)&& data.batteryP<20) {
        pluggedIn="😭"
    } else {
        pluggedIn="😎"
    }
    if (data.action == 'select') {
        $('#' + data.type + 'Status').text('Ready');
        $('#' + data.type + 'ScoutID').text(' (' + data.scoutID + ")" + " ["+ data.batteryP+ "%"+pluggedIn+"]");
    } else {
        $('#' + data.type + 'Status').text('...');
        $('#' + data.type + 'ScoutID').text('');
    }
    if (data.batteryP<20 && (!data.batteryPlug)){
        $('#' + data.type + 'Status').css("color", "red")
        $('#' + data.type + 'ScoutID').css("color", "red")
    } else if ((data.batteryPlug)){
        $('#' + data.type + 'Status').css("color", "green")
        $('#' + data.type + 'ScoutID').css("color", "green")
    }else{
        $('#' + data.type + 'Status').css("color", "white")
        $('#' + data.type + 'ScoutID').css("color", "white")
    }
});

// send the match number and the teams numbers to the scouts
$('button#sendInfo').click(function() {
    console.log('sending info');
    $('#sendInfo').text('Info sent!');
    socket.emit('scoutAssign', {
        matchNum: $('#matchNum').val(),
        red1: $('#red1teamNum').text(),
        red2: $('#red2teamNum').text(),
        red3: $('#red3teamNum').text(),
        blue1: $('#blue1teamNum').text(),
        blue2: $('#blue2teamNum').text(),
        blue3: $('#blue3teamNum').text()
    });
    $('#red1Status').text('Scouting');
    $('#red2Status').text('Scouting');
    $('#red3Status').text('Scouting');
    $('#blue1Status').text('Scouting');
    $('#blue2Status').text('Scouting');
    $('#blue3Status').text('Scouting');
    $('#redSuperStatus').text('Scouting');
    $('#blueSuperStatus').text('Scouting');
});

$('button#matchReset').click(function() {
    console.log('resetting match');
    socket.emit('matchReset', {matchNum: $('#matchNum').val()});
});

$('button#postData').click(function() {
    socket.emit('postData', {matchNum: $('#matchNum').val()});
    $('button#postData').prop('disabled', true);
    $('#postDataStatus').text('Waiting...')
});

socket.on('postDataStatus', function(data) {
    console.log(data);
    $('#postDataStatus').text(data.status);
    $('button#postData').prop('disabled', false);
});

// let the super scout know that the scouts have submitted (feature in testing)
socket.on('scoutSubmit', function(data) {
    console.log(data);
    // Lookup the row in the table where data.teamNum is, and update the state of the scout to be 'done'
    $('#scouterStatus tr').each(function() {
        // Normal scouts
        if ($(this).find('td:first').next().text() == data.teamNum) {
            $(this).find('td:last > span:first').text('Done');
        }
    });
    // Super scouts
    if (data.alliance == "red") {
        $("#redSuperStatus").text('Done');
    } else if (data.alliance == "blue") {
        $('#blueSuperStatus').text('Done');
    }
    // Refresh the DB tables in real-time
    fetchAndRender();
});

// Refresh DB viewer when server notifies DB updates
socket.on('scoutSubmit', function(data) {
    console.log('currentDBUpdated', data);
    fetchAndRender();
});

socket.on('matchReset', function(data) {
    console.log('oldDBUpdated', data);
    fetchAndRender();
});