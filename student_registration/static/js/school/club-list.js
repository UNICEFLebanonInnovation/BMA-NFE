
$(document).ready(function() {

    $( ".delete-club" ).on( "click", function(e) {

        e.preventDefault();

        var buttonId = $(this).attr("id");
        var clubId = $(this).data("club-id");
        var parentTR = $(this).closest('tr');

        var confirmed = confirm("Are you sure you want to delete this club?");
        requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        if (confirmed) {
            $.ajax({
                url: "/schools/club-delete/" + clubId + "/",
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
            console.log("User canceled deleting for club with ID: " + clubId);
        }
    } );

});

