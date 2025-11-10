
$(document).ready(function() {

    $( ".delete-visit" ).on( "click", function(e) {

        e.preventDefault();

        var buttonId = $(this).attr("id");
        var visitId = $(this).data("visit-id");
        var parentTR = $(this).closest('tr');

        var confirmed = confirm("Are you sure you want to delete this visit?");
        requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        if (confirmed) {
            $.ajax({
                url: "/schools/health-visit-delete/" + visitId + "/",
                type: "GET",
                headers: requestHeaders,
                success: function(data) {
                    console.log(parentTR.html());
                    parentTR.remove();
                },
                error: function(error) {
                    // Handle error if needed
                }
            });
        } else {
            console.log("User canceled deleting for visit with ID: " + visitId);
        }
    } );

});

