$(document).ready(function() {
    "use strict";
    $('.bingo-ticket .ticket-number').on('click', function(ev) {
        var target, pk, number;

        target = $(ev.target);
        pk = target.data('pk');
        number = target.data('number');
        console.log('click '+pk+' '+number);
        if (target.hasClass('mine') || !pk) {
            return;
        }
        ev.preventDefault();
        $('#confirm-dialog .modal-body').html('<p>Would you like to choose ticket ' +
                                              number + '?</p>');
        $('#confirm-dialog .modal-footer .yes-button').attr('href', target.attr('href'));
        $('#confirm-dialog').modal("show");
    });

    $('#confirm-dialog .modal-footer .yes-button').on('click', function(ev) {
        $('#confirm-dialog').modal("hide");
    });
});
