

$(document).ready(function() {

    $(document).on('click', '.download-report', function(e){
        e.preventDefault();

        var partner = $("#id_partner").val();
        var governorate = $("#id_adolescent__governorate").val();
        var district = $("#id_adolescent__district").val();
        var cadaster = $("#id_adolescent__cadaster").val();
        var adolescent_first_name = $("#id_adolescent__first_name").val();
        var adolescent_father_name = $("#id_adolescent__father_name").val();
        var adolescent_last_name = $("#id_adolescent__last_name").val();
        var adolescent_unicef_id = $("#id_adolescent__unicef_id").val();
        var adolescent_gender = $("#id_adolescent__gender").val();
        var adolescent_nationality = $("#id_adolescent__nationality").val();
        var adolescent_disability = $("#id_adolescent__disability").val();
        var adolescent_first_phone_number = $("#id_adolescent__first_phone_number").val();
        var master_program = $("#id_master_program").val();
        var sub_program = $("#id_sub_program").val();
        var donor = $("#id_donor").val();
        var program_document = $("#id_program_document").val();
        var start_date = $("#id_start_date").val();
        var end_date = $("#id_end_date").val();


        window.open("/youth/export/?partner=" + partner
                                + "&governorate=" + governorate
                                + "&district=" + district
                                + "&cadaster=" + cadaster
                                + "&adolescent_first_name=" + adolescent_first_name
                                + "&adolescent_father_name=" + adolescent_father_name
                                + "&adolescent_last_name=" + adolescent_last_name
                                + "&adolescent_unicef_id=" + adolescent_unicef_id
                                + "&adolescent_gender=" + adolescent_gender
                                + "&adolescent_nationality=" + adolescent_nationality
                                + "&adolescent_disability=" + adolescent_disability
                                + "&adolescent_first_phone_number=" + adolescent_first_phone_number
                                + "&master_program=" + master_program
                                + "&sub_program=" + sub_program
                                + "&donor=" + donor
                                + "&program_document=" + program_document
                                + "&start_date=" + start_date
                                + "&end_date=" + end_date  ,
            "_blank")
    });

    $( ".delete-student" ).on( "click", function(e) {

        e.preventDefault();

        var buttonId = $(this).attr("id");
        var registrationId = $(this).data("registration-id");
        var parentTR = $(this).closest('tr');

        var confirmed = confirm("Are you sure you want to disable this student?");
        requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        if (confirmed) {
            $.ajax({
                url: "/youth/child-mark-delete/" + registrationId + "/",
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
            console.log("User canceled disabling student with ID: " + studentId);
        }
    } );

    $(document).on('click', '.download-center-report', function(e){
        e.preventDefault();

        var center_name = $("#id_name").val();
        var center_type = $("#id_type").val();
        var center_governorate = $("#id_governorate").val();

        window.open("/locations/export/?center_name=" + center_name
                                + "&center_type=" + center_type
                                + "&center_governorate=" + center_governorate ,
            "_blank")
    });
});

