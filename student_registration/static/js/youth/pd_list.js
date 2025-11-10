

$(document).ready(function() {

    $(document).on('click', '.download-report', function(e){
        e.preventDefault();

        var partner = $("#id_partner").val();
        var funded_by = $("#id_funded_by").val();
        var project_status = $("#id_project_status").val();
        var project_code = $("#id_project_code").val();
        var project_name = $("#id_project_name").val();
        var implementing_partners = $("#id_implementing_partners").val();
        var focal_point = $("#id_focal_point").val();
        var start_date = $("#id_start_date").val();
        var end_date = $("#id_end_date").val();
        var donor = $("#id_donor").val();
        var master_program = $("#id_master_program").val();


        window.open("/youth/export-pd/?partner=" + partner
                                + "&funded_by=" + funded_by
                                + "&project_status=" + project_status
                                + "&project_code=" + project_code
                                + "&project_name=" + project_name
                                + "&implementing_partners=" + implementing_partners
                                + "&focal_point=" + focal_point
                                + "&start_date=" + start_date
                                + "&end_date=" + end_date
                                + "&donor=" + donor
                                + "&master_program=" + master_program ,
            "_blank")
    });

});

