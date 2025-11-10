
$(document).ready(function() {

    if($('#id_date_first_visit').length == 1) {
        $('#id_date_first_visit').datepicker({dateFormat: "yy-mm-dd"});
    }

    if($('#id_date_last_visit').length == 1) {
        $('#id_date_last_visit').datepicker({dateFormat: "yy-mm-dd"});
    }

});



