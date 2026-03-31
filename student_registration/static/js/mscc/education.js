

$(document).ready(function() {
    reorganizeForm();

if ($('#id_dropout_date').length === 1 && $.fn.datepicker) {
    $('#id_dropout_date').datepicker({ dateFormat: "yy-mm-dd" });
}

if ($('#id_registration_date').length === 1 && $.fn.datepicker) {
    $('#id_registration_date').datepicker({ dateFormat: "yy-mm-dd" });
}

    $(document).on('change', '#id_education_program', function(){
        reorganizeForm();
    });

    $(document).on('change', '#id_education_status', function(){
        reorganizeForm();
    });
});

function reorganizeForm()
{
//    Education Status
   var education_status = $('select#id_education_status').val();

    console.log('education_status value =', education_status);
    console.log('dropout wrapper found =', $('#div_id_dropout_date').length);
    console.log('dropout input found =', $('#id_dropout_date').length);

    $('div#div_id_dropout_date').addClass('d-none');
    $('#span_dropout_date').addClass('d-none');

if (education_status && education_status.includes('not attending')) {
    console.log('showing dropout date');
    $('#div_id_dropout_date').removeClass('d-none');
    $('#span_dropout_date').removeClass('d-none');

    $('#id_dropout_date').addClass('error-field');
    $('#id_dropout_date').prop('required', true);
}
else {
    console.log('hiding dropout date');
    $('#div_id_dropout_date').addClass('d-none');

    $('#id_dropout_date').removeClass('error-field');
    $('#id_dropout_date').prop('required', false);
    $('#id_dropout_date').val('');
}

//   Education Program
   var education_program = $('select#id_education_program').val();
    $('div#div_id_catch_up_registered').addClass('d-none');
    $('#span_catch_up_registered').addClass('d-none');

    const CatchUpPrograms = [
      'BLN Catch-up',
      'ABLN Catch-up',
      'CBECE Catch-up',
      'YBLN Catch-up'
    ];


    if (CatchUpPrograms.includes(education_program)) {
        $('#div_id_catch_up_registered').removeClass('d-none');
        $('#span_catch_up_registered').removeClass('d-none');
        $('#id_catch_up_registered').addClass('error-field');
    }
    else
    {
        $('div#div_id_catch_up_registered').addClass('d-none');
        $('#id_catch_up_registered').removeClass('error-field');
        $('#id_catch_up_registered').val('');
    }
}

