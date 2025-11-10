

$(document).ready(function() {
    reorganizeForm();

    if($(document).find('#id_miss_school_date').length == 1) {
        $('#id_miss_school_date').datepicker({dateFormat: "yy-mm-dd"});
    }
     if($(document).find('#id_first_attendance_date').length == 1) {
        $('#id_first_attendance_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', 'select#id_education_status', function(){
        reorganizeForm();
    });
});

function reorganizeForm()
{
    var student_age = $('#id_student_age').val();
    var education_status = $('select#id_education_status').val();
    $('div#div_id_miss_school_date').addClass('d-none');
    $('#span_miss_school_date').addClass('d-none');
    $('div#div_id_dropout_program').addClass('d-none');
    $('#span_dropout_program').addClass('d-none');

    if(education_status != 'out of school'){
        $('#div_id_miss_school_date').removeClass('d-none');
        $('#span_miss_school_date').removeClass('d-none');
        $('div#div_id_dropout_program').removeClass('d-none');
        $('#span_dropout_program').removeClass('d-none');
    }
    if (student_age >= 16){
        $('#youth').removeClass('d-none');
    }
    else{
        $('#youth').addClass('d-none');
    }
}



function urlParam(name){
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	if (results && results.length){
        return results[1] || 0;
    }
    return 0;
}
