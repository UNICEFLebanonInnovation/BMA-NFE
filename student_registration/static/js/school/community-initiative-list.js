
$(document).ready(function() {

    $( ".delete-initiative" ).on( "click", function(e) {

        e.preventDefault();

        var buttonId = $(this).attr("id");
        var initiativeId = $(this).data("initiative-id");
        var parentTR = $(this).closest('tr');

        var confirmed = confirm("Are you sure you want to delete this initiative?");
        requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        if (confirmed) {
            $.ajax({
                url: "/schools/community-initiative-delete/" + initiativeId + "/",
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
            console.log("User canceled deleting for initiative with ID: " + initiativeId);
        }
    } );

});

