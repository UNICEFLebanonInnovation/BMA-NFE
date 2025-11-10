(function($){
    window.showModal = function(message){
        var modal = $('#alertModal');
        if(!modal.length){
            var modalHtml = '<div class="modal fade" id="alertModal" tabindex="-1" role="dialog">'
                + '<div class="modal-dialog" role="document">'
                + '<div class="modal-content">'
                + '<div class="modal-body"></div>'
                + '<div class="modal-footer">'
                + '<button type="button" class="btn btn-primary" data-dismiss="modal">OK</button>'
                + '</div></div></div></div>';
            $('body').append(modalHtml);
            modal = $('#alertModal');
        }
        modal.find('.modal-body').text(message);
        modal.modal('show');
    };
})(jQuery);
