$(document).ready(function() {

    $(document).on('click', '.download-report', function(e){

        e.preventDefault();
        requestHeaders = getHeader();

        $(".downloading-message").show();
        $('.download-report').addClass('disabled');

        $.ajax({
            url: "/schools/school-export-background/",
            type: "GET",
            headers: requestHeaders,
            success: function(data) {
               $(".downloading-message").hide();
               $('.download-report').removeClass('disabled');
               window.open("/mscc/export-download/" + data,
                           "_blank");

            },
            error: function(error) {
            }
        });

    });

});
