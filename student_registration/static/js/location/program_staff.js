

$(document).ready(function() {

    $('.delete-program-staff').click(function(event) {
        event.preventDefault();
        var programStaffId = $(this).data('id');
        var trToDelete = $(this).closest('tr');

        var confirmed = window.confirm("Are you sure you want to delete this staff member?");
        requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';
        if (confirmed) {
        $.ajax({
            url: "/locations/Program-Staff-Delete/" + programStaffId + "/",
            type: "GET",
            headers: requestHeaders,
            success: function(data) {
                console.log(trToDelete.html());
                trToDelete.remove();
            },
            error: function(error) {
                console.log('An error occurred while making the request.');
            }
        });
        } else {
            console.log("User canceled marking as deleted for student with ID: " + studentId);
        }
        });
    });



