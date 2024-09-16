
socket.on('message', function(data) {
    $('#chat').val($('#chat').val() + data.msg + '\n');
    $('#chat').scrollTop($('#chat')[0].scrollHeight);
});

$('#text').keypress(function(e) {
    var code = e.keyCode || e.which;
    if (code == 13) {
        text = $('#text').val();
        $('#text').val('');
        socket.emit('message', {msg: text});
    }
});

