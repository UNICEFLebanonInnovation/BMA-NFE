

$(document).ready(function() {


    const updateMsccListTableWidth = () => {
        const $tableContainer = $('.table-list');

        if (!$tableContainer.length) {
            return;
        }

        const viewportWidth = window.innerWidth || document.documentElement.clientWidth;

        let widthValue = '100%';

        if (viewportWidth >= 1400) {
            widthValue = 'calc(100vw - 9rem)';
        } else if (viewportWidth >= 1200) {
            widthValue = 'calc(100vw - 7rem)';
        } else if (viewportWidth >= 992) {
            widthValue = 'calc(100vw - 5rem)';
        } else if (viewportWidth >= 768) {
            widthValue = 'calc(100vw - 3rem)';
        } else if (viewportWidth >= 576) {
            widthValue = 'calc(100vw - 2rem)';
        }

        $tableContainer.css('--mscc-table-width', widthValue);
    };

    updateMsccListTableWidth();
    $(window).on('resize orientationchange', updateMsccListTableWidth);

    $(document).on('shown.bs.modal', function(){
        $('.modal-backdrop').not(':last').remove();
    });

    $( ".delete-student" ).on( "click", function(e) {
        e.preventDefault();
        var registrationId = $(this).data("registration-id");
        var parentTR = $(this).closest('tr');
        var modal = $('#deleteConfirmModal');
        modal.data('registrationId', registrationId);
        modal.data('parentTR', parentTR);
        modal.modal('show');
    } );

    $(document).on('click', '#deleteConfirmModal .confirm-delete', function(){
        var modal = $('#deleteConfirmModal');
        var registrationId = modal.data('registrationId');
        var parentTR = modal.data('parentTR');
        requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';
        $.ajax({
            url: "/mscc/child-mark-delete/" + registrationId + "/",
            type: "GET",
            headers: requestHeaders,
            success: function(data) {
                parentTR.remove();
            },
            error: function(error) {
                // Handle error if needed
            },
            complete: function(){
                modal.modal('hide');
            }
        });
    });


    $(document).on('click', '.download-center-report', function(e){
        e.preventDefault();

        var center_name = $("#id_name").val();
        var center_type = $("#id_type").val();
        var center_governorate = $("#id_governorate").val();

        requestHeaders = getHeader();

        $(".downloading-message").show();
        $('.download-center-report').addClass('disabled');

        $.ajax({
            url: "/locations/export-center-background/?center_name=" + center_name
                                + "&center_type=" + center_type
                                + "&center_governorate=" + center_governorate ,
            type: "GET",
            headers: requestHeaders,
            success: function(data) {

               $(".downloading-message").hide();
               $('.download-center-report').removeClass('disabled');
               window.open("/mscc/export-download/" + data,
                           "_blank");

            },
            error: function(error) {
                // Handle error if needed
            }
        });

    });

    $(document).on('click', '.download-report', function(e){
        e.preventDefault();

        var nationality = $("#id_child__nationality").val();
        var first_name = $("#id_child__first_name").val();
        var last_name = $("#id_child__last_name").val();
        var father_name = $("#id_child__father_name").val();
        var mother_fullname = $("#id_child__mother_fullname").val();
        var round = $("#id_round").val();
        if(!round){
            showModal("Cycle is not selected. Please select a cycle before exporting data.");
            return;
        }

        requestHeaders = getHeader();
        $(".downloading-message").show();
        $('.download-report').addClass('disabled');

        $.ajax({
            url: "/mscc/export-list-background/?nationality=" + nationality
                                + "&first_name=" + first_name
                                + "&last_name=" + last_name
                                + "&father_name=" + father_name
                               + "&mother_fullname=" + mother_fullname
                               + "&round=" + round,
            type: "GET",
            headers: requestHeaders,
            success: function() {
               $(".downloading-message").hide();
               $('.download-report').removeClass('disabled');
               showModal('Export started. You will be notified when ready.');
            },
            error: function() {
               showModal('Failed to start export. Please try again later.');
            }
        });

    });

});

    $(document).on('click', '.download-report-async', function(e){
        e.preventDefault();
        $('#exportOptionsModal').modal('show');
    });

    $(document).on('click', '#exportOptionsModal .start-export', function(){
        var nationality = $("#id_child__nationality").val();
        var first_name = $("#id_child__first_name").val();
        var last_name = $("#id_child__last_name").val();
        var father_name = $("#id_child__father_name").val();
        var mother_fullname = $("#id_child__mother_fullname").val();
        var round = $("#id_round").val();
        var button = $(this);
        var originalHtml = button.html();
        button.prop('disabled', true);
        button.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...');
        if(!round){
            $('#exportOptionsModal').modal('hide');
            showModal('Cycle is not selected. Please select a cycle before exporting data.');
            button.prop('disabled', false);
            button.html(originalHtml);
            return;
        }
        requestHeaders = getHeader();
        $.ajax({
            url: "/mscc/export-list-background/?nationality=" + nationality
                                + "&first_name=" + first_name
                                + "&last_name=" + last_name
                                + "&father_name=" + father_name
                               + "&mother_fullname=" + mother_fullname
                               + "&round=" + round,
            type: 'GET',
            headers: requestHeaders,
            success: function(){
                $('#exportOptionsModal').modal('hide');
                showModal('Export started. You will be notified when ready.');
            },
            error: function(){
                showModal('Failed to start export. Please try again later.');
            },
            complete: function(){
                button.prop('disabled', false);
                button.html(originalHtml);
            }
        });
    });

