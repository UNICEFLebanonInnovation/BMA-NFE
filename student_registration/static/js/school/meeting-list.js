
$(document).ready(function() {

    $( ".delete-meeting" ).on( "click", function(e) {

        e.preventDefault();

        var schoolId = $(this).data("school-id");
        var deleteUrl = $(this).attr("href");

        var confirmed = confirm("Are you sure you want to delete this meeting?");
        requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        if (confirmed) {
            $.ajax({
                url: deleteUrl,
                type: "GET",
                headers: requestHeaders,
                success: function(data) {
                    var redirectUrl = "/schools/meeting-list/" + schoolId + "/";
                    window.location.href = redirectUrl;
                },
            });
        } else {
            console.log("User canceled deleting for meeting with ID: " + meetingId);
        }
    } );

});

