

$(document).ready(function(){
    reorganizeForm();

    if($(document).find('#id_adolescent_dropout_date').length == 1) {
        $('#id_adolescent_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', 'select#id_participate_volunteering, select#id_yfs_course_completed, select#id_participate_community_initiatives, select#id_adolescent_attendance' , function(){
       reorganizeForm();
    });
});


function reorganizeForm()
{
    var participate_volunteering = $('#id_participate_volunteering').val();

    if (participate_volunteering == 'Yes'){
        $('div#div_id_volunteering_specify').removeClass('d-none');
        if ($('#id_volunteering_specify').val()== null || $('#id_volunteering_specify').val()=='')
        {
            $('#id_volunteering_specify').addClass('error-field');
        }
    }
    else{
        $('#id_volunteering_specify').val('');
        $('div#div_id_volunteering_specify').addClass('d-none');
        $('#id_volunteering_specify').removeClass('error-field');
    }

    var yfs_course_completed = $('#id_yfs_course_completed').val();
    if (yfs_course_completed == 'Yes'){
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

    var participate_community_initiatives = $('#id_participate_community_initiatives').val();
    if (participate_community_initiatives == 'Yes'){
        $('div#div_id_community_initiatives_specify').removeClass('d-none');
        if ($('#id_community_initiatives_specify').val()== null || $('#id_community_initiatives_specify').val()=='')
        {
            $('#id_community_initiatives_specify').addClass('error-field');
        }
    }
    else{
        $('#id_community_initiatives_specify').val('');
        $('div#div_id_community_initiatives_specify').addClass('d-none');
        $('#id_community_initiatives_specify').removeClass('error-field');
    }

    var adolescent_attendance = $('#id_adolescent_attendance').val();
    if (adolescent_attendance == 'Dropout'){
        $('div#div_id_adolescent_dropout_reason').removeClass('d-none');
        if ($('#id_adolescent_dropout_reason').val()== null || $('#id_adolescent_dropout_reason').val()=='')
        {
            $('#id_adolescent_dropout_reason').addClass('error-field');
        }

        $('div#div_id_adolescent_dropout_date').removeClass('d-none');
        if ($('#id_adolescent_dropout_date').val()== null || $('#id_adolescent_dropout_date').val()=='')
        {
            $('#id_adolescent_dropout_date').addClass('error-field');
        }
        $('#').addClass('error-field');
    }
    else{
        $('#id_adolescent_dropout_reason').val('');
        $('div#div_id_adolescent_dropout_reason').addClass('d-none');
        $('#id_adolescent_dropout_reason').removeClass('error-field');

        $('#id_adolescent_dropout_date').val('');
        $('div#div_id_adolescent_dropout_date').addClass('d-none');
        $('#id_adolescent_dropout_date').removeClass('error-field');
    }
  }

