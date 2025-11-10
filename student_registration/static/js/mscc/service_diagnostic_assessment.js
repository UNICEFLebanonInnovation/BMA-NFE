

$(document).ready(function(){
       reorganizeForm();

    $(document).on('change', ' select#id_pre_attended_arabic, select#id_pre_attended_language,  select#id_pre_attended_math' , function(){
       reorganizeForm();
    });


});


function reorganizeForm()
{
    var attended_arabic = $('select#id_pre_attended_arabic').val();
    var attended_foreign_language = $('select#id_pre_attended_language').val();
    var attended_math = $('select#id_pre_attended_math').val();


    if(attended_arabic == 'Yes'){
        $('div#div_id_pre_arabic_grade').removeClass('d-none');
        if ($('#id_pre_arabic_grade').val()== null || $('#id_pre_arabic_grade').val()=='')
        {
            $('#id_pre_arabic_grade').addClass('error-field');
        }
        $('div#div_id_pre_modality_arabic').removeClass('d-none');
        if ($('#id_pre_modality_arabic').val()== null || $('#id_pre_modality_arabic').val()=='')
        {
            $('#id_pre_modality_arabic').addClass('error-field');
        }

    }
    else{
        $('#id_pre_arabic_grade').val(0);
        $('select#id_pre_modality_arabic').val("");

        $('div#div_id_pre_arabic_grade').addClass('d-none');
        $('#id_pre_arabic_grade').removeClass('error-field');

        $('div#div_id_pre_modality_arabic').addClass('d-none');
        $('#id_pre_modality_arabic').removeClass('error-field');
        $('.grd-arabic').prop('required',true);
    }

    // attended_foreign_language
    if(attended_foreign_language == 'Yes'){
        $('div#div_id_pre_language_grade').removeClass('d-none');
        if ($('#id_pre_language_grade').val()== null || $('#id_pre_language_grade').val()=='')
        {
            $('#id_pre_language_grade').addClass('error-field');
        }
        $('div#div_id_pre_modality_language').removeClass('d-none');
        if ($('#id_pre_modality_language').val()== null || $('#id_pre_modality_language').val()=='')
        {
            $('#id_pre_modality_language').addClass('error-field');
        }

    }
    else{
        $('#id_pre_language_grade').val(0);
        $('div#div_id_pre_language_grade').addClass('d-none');
        $('#id_pre_language_grade').removeClass('error-field');
        $('select#id_pre_modality_language').val("");
        $('div#div_id_pre_modality_language').addClass('d-none');
        $('#id_pre_modality_language').removeClass('error-field');
    }
    // attended_math
    if(attended_math == 'Yes'){
        $('div#div_id_pre_math_grade').removeClass('d-none');
        if ($('#id_pre_math_grade').val()== null || $('#id_pre_math_grade').val()=='')
        {
            $('#id_pre_math_grade').addClass('error-field');
        }
        $('div#div_id_pre_modality_math').removeClass('d-none');
        if ($('#id_pre_modality_math').val()== null || $('#id_pre_modality_math').val()=='')
        {
            $('#id_pre_modality_math').addClass('error-field');
        }
    }
    else{
        $('#id_pre_math_grade').val(0);
        $('div#div_id_pre_math_grade').addClass('d-none');
        $('#id_pre_math_grade').removeClass('error-field');
        $('select#id_pre_modality_math').val("");
        $('div#div_id_pre_modality_math').addClass('d-none');
        $('#id_pre_math_grade').removeClass('error-field');
    }
  }
