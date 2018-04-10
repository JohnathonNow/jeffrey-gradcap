const cell_prefix = 'cell_';

var v = 0;
var zoom = 1024;

function read() {
    $.get( "read", {'v': v}, function(data) {
        console.log(data);
        var p = JSON.parse(data);
        if (p['status'] === 'success') {
            if (v < p['payload']['v']) {
                var colors = p['payload']['colors']
                for (var key in colors) {
                    $("#" + cell_prefix + key).css('background-color', colors[key]);
                }
            }
            v = p['payload']['v'];
        }
        setTimeout(read, 1000);
    }).fail(function() {
        setTimeout(read, 50);
    });
}

function chzoom(w) {
    zoom *= w;
    $('#zoomable').css('width', zoom+"px");
    $('#zoomable').css('height', zoom+"px");
}

$(function() {
    var palette = $('ul');
    for (var i = 0; i < 32*32; i++) {
        var n = $('<li />').css('background-color', '#000000');
        n.attr('id', cell_prefix + i);
        palette.append(n);
    }

    $('li').on('click', function(e) {
        var color = $('#brush').val();
        var id = $(this).attr('id').split('_')[1];

        $.get("write", {'id': id, 'color': color});
        $(this).css('background-color', color);
    });

    zoom = $('#zoomable').outerWidth(true);

    $('#zoomout').on('click', function(e) {
        chzoom(1/1.2);
    });

    $('#zoomin').on('click', function(e) {
        chzoom(1.2);
    });

    read();
});
