

$(document).ready(function(){
    reorganizeForm();

    $(document).on('change', 'select#id_social_course' , function(){
       reorganizeForm();
    });
});


function reorganizeForm()
{
    $('div.course').addClass('d-none');
    var social_course = $('#id_social_course').val();

    if (social_course == 'Yes'){
        $('div.course').removeClass('d-none');
    }
    else
    {
        $('#id_trainer_showed_knowledge').val('');
        $('#id_trainer_encouraged_discussions').val('');
        $('#id_trainer_provided_feedback').val('');
        $('#id_trainer_patient_helped').val('');
        $('#id_training_part_useful').val('');
        $('#id_training_part_difficult').val('');
        $('#id_course_feel').val('');
    }
  }

