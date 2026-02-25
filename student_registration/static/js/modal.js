(function($){
    window.showModal = function(message){
        var modalEl = document.getElementById('alertModal');
        if(!modalEl){
            var modalHtml = '<div class="modal fade" id="alertModal" tabindex="-1" aria-hidden="true">'
                + '<div class="modal-dialog" role="document">'
                + '<div class="modal-content">'
                + '<div class="modal-body py-4 text-center fs-5"></div>'
                + '<div class="modal-footer border-top-0 justify-content-center">'
                + '<button type="button" class="btn btn-primary px-5 fw-bold" data-bs-dismiss="modal">OK</button>'
                + '</div></div></div></div>';
            $('body').append(modalHtml);
            modalEl = document.getElementById('alertModal');
        }
        $(modalEl).find('.modal-body').text(message);
        var bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
        bsModal.show();
    };
})(jQuery);
