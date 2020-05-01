$(document).ready(function() {
    "use strict";
    function load_state(index, ticket) {
        var game_id = $(ticket).data("game-id");
        var ticket_number = $(ticket).data("ticket-number");
        var key = "ticket-" + game_id + "-" + ticket_number;
        var data = localStorage.get(key);
        if (data !== null) {
            data = JSON.parse(data);
        }
    }

    $('.bingo-cell').on('click', function(ev) {
        console.log('click');
        $(ev.target).parentsUntil("tr").toggleClass('ticked');
    });
    $('.bingo-ticket').each(load_state);
});
