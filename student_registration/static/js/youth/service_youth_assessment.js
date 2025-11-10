

$(document).ready(function(){
    reorganizeForm();

    $(document).on('change', 'select#id_undertake_post_diagnostic, select#id_participate_volunteering, select#id_compelete_yfs_course' , function(){
       reorganizeForm();
    });
});


function reorganizeForm()
{
    var undertake_post_diagnostic = $('#id_undertake_post_diagnostic').val();
    var participate_volunteering = $('#id_participate_volunteering').val();
    var compelete_yfs_course = $('#id_compelete_yfs_course').val();

    if (undertake_post_diagnostic == 'Yes'){
        $('div#div_id_receive_passing_grade').removeClass('d-none');
        if ($('#id_receive_passing_grade').val()== null || $('#id_receive_passing_grade').val()=='')
        {
            $('#id_receive_passing_grade').addClass('error-field');
        }
    }
    else{
        $('#id_receive_passing_grade').val('');
        $('div#div_id_receive_passing_grade').addClass('d-none');
        $('#id_receive_passing_grade').removeClass('error-field');
    }

    if (participate_volunteering == 'Yes'){
        $('div#div_id_volunteering_opportunity').removeClass('d-none');
        if ($('#id_volunteering_opportunity').val()== null || $('#id_volunteering_opportunity').val()=='')
        {
            $('#id_volunteering_opportunity').addClass('error-field');
        }
    }
    else{
        $('#id_volunteering_opportunity').val('');
        $('div#div_id_volunteering_opportunity').addClass('d-none');
        $('#id_volunteering_opportunity').removeClass('error-field');
    }

    if (compelete_yfs_course == 'Yes'){
        $('div#div_id_training_material').removeClass('d-none');
        if ($('#id_training_material').val()== null || $('#id_training_material').val()=='')
        {
            $('#id_training_material').addClass('error-field');
        }
    }
    else{
        $('#id_training_material').val('');
        $('div#div_id_training_material').addClass('d-none');
        $('#id_training_material').removeClass('error-field');
    }
  }

