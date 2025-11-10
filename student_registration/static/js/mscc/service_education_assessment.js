

$(document).ready(function(){
       reorganizeForm();

    $(document).on('change', ' select#id_post_attended_arabic, select#id_post_attended_language,  select#id_post_attended_math,  ' +
        'select#id_post_test_done,  select#id_barriers ' , function(){
       reorganizeForm();
    });
});


function reorganizeForm()
{
    var barriers = $('select#id_barriers').val();
    if(barriers == 'Other'){
        $('div#div_id_barriers_other').removeClass('d-none');
        if ($('#id_barriers_other').val()== null || $('#id_barriers_other').val()=='')
        {
            $('#id_barriers_other').addClass('error-field');
        }
    }
    else{
        $('#id_barriers_other').val('');
        $('div#div_id_barriers_other').addClass('d-none');
        $('#id_barriers_other').removeClass('error-field');
    }

    var test_done = $('select#id_post_test_done').val();
    var attended_arabic = $('select#id_post_attended_arabic').val();
    var attended_foreign_language = $('select#id_post_attended_language').val();
    var attended_math = $('select#id_post_attended_math').val();

    if(test_done == 'Yes'){
       $('div.grades').removeClass('d-none');
        // attended_arabic
        if(attended_arabic == 'Yes'){
            $('div#div_id_post_arabic_grade').removeClass('d-none');
            if ($('#id_post_arabic_grade').val()== null || $('#id_post_arabic_grade').val()=='')
            {
                $('#id_post_arabic_grade').addClass('error-field');
            }
            $('div#div_id_post_modality_arabic').removeClass('d-none');
            if ($('#id_post_modality_arabic').val()== null || $('#id_post_modality_arabic').val()=='')
            {
                $('#id_post_modality_arabic').addClass('error-field');
            }
        }
        else{
            $('#id_post_arabic_grade').val(0);
            $('select#id_post_modality_arabic').val("");

            $('div#div_id_post_arabic_grade').addClass('d-none');
            $('#id_post_arabic_grade').removeClass('error-field');
            $('div#div_id_post_modality_arabic').addClass('d-none');
            $('#id_post_modality_arabic').removeClass('error-field');
        }

        // attended_foreign_language
        if(attended_foreign_language == 'Yes'){
            $('div#div_id_post_language_grade').removeClass('d-none');
            if ($('#id_post_language_grade').val()== null || $('#id_post_language_grade').val()=='')
            {
                $('#id_post_language_grade').addClass('error-field');
            }
            $('div#div_id_post_modality_language').removeClass('d-none');
            if ($('#id_post_modality_language').val()== null || $('#id_post_modality_language').val()=='')
            {
                $('#id_post_modality_language').addClass('error-field');
            }

        }
        else{
            $('#id_post_language_grade').val(0);
            $('div#div_id_post_language_grade').addClass('d-none');
            $('#id_post_language_grade').removeClass('error-field');
            $('select#id_post_modality_language').val("");
            $('div#div_id_post_modality_language').addClass('d-none');
            $('#id_post_modality_language').removeClass('error-field');
        }
        // attended_math
        if(attended_math == 'Yes'){
            $('div#div_id_post_math_grade').removeClass('d-none');
            if ($('#id_post_math_grade').val()== null || $('#id_post_math_grade').val()=='')
            {
                $('#id_post_math_grade').addClass('error-field');
            }
            $('div#div_id_post_modality_math').removeClass('d-none');
            if ($('#id_post_modality_math').val()== null || $('#id_post_modality_math').val()=='')
            {
                $('#id_post_modality_math').addClass('error-field');
            }
        }
        else{
            $('#id_post_math_grade').val(0);
            $('div#div_id_post_math_grade').addClass('d-none');
            $('#id_post_math_grade').removeClass('error-field');
            $('select#id_post_modality_math').val("");
            $('div#div_id_post_modality_math').addClass('d-none');
            $('#id_post_math_grade').removeClass('error-field');
        }
    }
    else
    {
        $('div.grades').addClass('d-none');
        $('#id_post_arabic_grade').val(0);
        $('#id_post_language_grade').val(0);
        $('#id_post_math_grade').val(0);
    }

  }

