

$(document).ready(function(){
    reorganizeForm();

    if($(document).find('#id_dropout_date').length == 1) {
        $('#id_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', 'select#id_follow_up_type, select#id_follow_up_result, select#id_parent_attended_meeting, select#id_caregiver_attended, select#id_pfss_sessions' , function(){
       reorganizeForm();
    });
});


function reorganizeForm()
{
//  pfss_sessions
    var pfss_sessions =  $('select#id_pfss_sessions').val();
    $('div#div_id_pfss_sessions_number').addClass('d-none');
    if(pfss_sessions == 'Yes'){
        $('#div_id_pfss_sessions_number').removeClass('d-none');
        if ($('#id_pfss_sessions_number').val() == null || $('#id_pfss_sessions_number').val()=='' || $('#id_pfss_sessions_number').val()=='0')
        {
            $('#id_pfss_sessions_number').addClass('error-field');
        }
    }else{
        $('#id_pfss_sessions_number').val(0);
    }


//    Dropout
    var follow_up_result = $('select#id_follow_up_result').val();
    if (follow_up_result == 'Dropout/No Interest'){
        $('#div_id_dropout_reason').removeClass('d-none');
        $('#span_dropout_reason').removeClass('d-none');
        if ($('#id_dropout_reason').val()== null || $('#id_dropout_reason').val()=='')
        {
            $('#id_dropout_reason').addClass('error-field');
        }

        $('#div_id_dropout_date').removeClass('d-none');
        $('#span_dropout_date').removeClass('d-none');
        if ($('#id_dropout_date').val()== null || $('#id_dropout_date').val()=='')
        {
            $('#id_dropout_date').addClass('error-field');
        }
    }
    else
    {
        $('div#div_id_dropout_reason').addClass('d-none');
        $('#span_dropout_reason').addClass('d-none');
        $('#id_dropout_reason').removeClass('error-field');
        $('#id_dropout_reason').val('');

        $('div#div_id_dropout_date').addClass('d-none');
        $('#span_dropout_date').addClass('d-none');
        $('#id_dropout_date').removeClass('error-field');
        $('#id_dropout_date').val('');
    }

//    Parents meeting
    var parent_attended_meeting = $('select#id_parent_attended_meeting').val();
    if (parent_attended_meeting == 'Yes'){
        $('#div_id_meeting_type').removeClass('d-none');
        $('#span_meeting_type').removeClass('d-none');
        if ($('#id_meeting_type').val()== null || $('#id_meeting_type').val()=='')
        {
            $('#id_meeting_type').addClass('error-field');
        }

        $('#div_id_meeting_number').removeClass('d-none');
        $('#span_meeting_number').removeClass('d-none');
        if ($('#id_meeting_number').val() == null || $('#id_meeting_number').val()=='' || $('#id_meeting_number').val()=='0')
        {
            $('#id_meeting_number').addClass('error-field');
        }

        $('#div_id_meeting_modality').removeClass('d-none');
        $('#span_meeting_modality').removeClass('d-none');
        if ($('#id_meeting_modality').val()== null || $('#id_meeting_modality').val()=='')
        {
            $('#id_meeting_modality').addClass('error-field');
        }

        $('#div_id_caregiver_attended').removeClass('d-none');
        $('#span_caregiver_attended').removeClass('d-none');
        if ($($('#id_caregiver_attended').val()== null || '#id_caregiver_attended').val()=='')
        {
            $('#id_caregiver_attended').addClass('error-field');
        }

        var caregiver_attended = $('select#id_caregiver_attended').val();
        if (caregiver_attended=='Other'){
            $('#div_id_caregiver_attended_other').removeClass('d-none');
            $('#span_caregiver_attended_other').removeClass('d-none');
            if ($('#id_caregiver_attended_other').val()== null || $('#id_caregiver_attended_other').val()=='')
            {
                $('#id_caregiver_attended_other').addClass('error-field');
            }
        }
        else
        {
            $('div#div_id_caregiver_attended_other').addClass('d-none');
            $('#span_caregiver_attended_other').addClass('d-none');
            $('#id_caregiver_attended_other').removeClass('error-field');
            $('#id_caregiver_attended_other').val('');
        }
    }
    else
    {
        $('div#div_id_meeting_type').addClass('d-none');
        $('#span_meeting_type').addClass('d-none');
        $('#id_meeting_type').removeClass('error-field');
        $('#id_meeting_type').val('');

        $('div#div_id_meeting_number').addClass('d-none');
        $('#span_meeting_number').addClass('d-none');
        $('#id_meeting_number').removeClass('error-field');
        $('#id_meeting_number').val(0);

        $('div#div_id_meeting_modality').addClass('d-none');
        $('#span_meeting_modality').addClass('d-none');
        $('#id_meeting_modality').removeClass('error-field');
        $('#id_meeting_modality').val('');

        $('#span_caregiver_attended').addClass('d-none');
        $('div#div_id_caregiver_attended').addClass('d-none');
        $('#id_caregiver_attended').removeClass('error-field');
        $('#id_caregiver_attended').val('');

        $('#span_caregiver_attended_other').addClass('d-none');
        $('div#div_id_caregiver_attended_other').addClass('d-none');
        $('#id_caregiver_attended_other').removeClass('error-field');
        $('#id_caregiver_attended_other').val('');
    }
  }

