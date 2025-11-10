

$(document).ready(function(){
    reorganizeForm();

    $(document).on('change', 'select#id_sports_taken, select#id_life_skills_taken, select#id_youth_lead_initiatives_taken' , function(){
       reorganizeForm();
    });
});


function reorganizeForm()
{
    var sports_taken = $('#id_sports_taken').val();

    if (sports_taken == 'Yes'){
        $('div#div_id_sports_session_number').removeClass('d-none');
        if ($('#id_sports_session_number').val()== null || $('#id_sports_session_number').val()=='')
        {
            $('#id_sports_session_number').addClass('error-field');
        }
    }
    else{
        $('#id_sports_session_number').val('');
        $('div#div_id_sports_session_number').addClass('d-none');
        $('#id_sports_session_number').removeClass('error-field');
    }

    var life_skills_taken = $('#id_life_skills_taken').val();
    if (life_skills_taken == 'Yes'){
        $('div#div_id_life_skills_number').removeClass('d-none');
        if ($('#id_life_skills_number').val()== null || $('#id_life_skills_number').val()=='')
        {
            $('#id_life_skills_number').addClass('error-field');
        }
    }
    else{
        $('#id_life_skills_number').val('');
        $('div#div_id_life_skills_number').addClass('d-none');
        $('#id_life_skills_number').removeClass('error-field');
    }

    var youth_lead_initiatives_taken = $('#id_youth_lead_initiatives_taken').val();
    if (youth_lead_initiatives_taken == 'Yes'){
        $('div#div_id_youth_lead_initiatives_number').removeClass('d-none');
        if ($('#id_youth_lead_initiatives_number').val()== null || $('#id_youth_lead_initiatives_number').val()=='')
        {
            $('#id_youth_lead_initiatives_number').addClass('error-field');
        }
    }
    else{
        $('#id_youth_lead_initiatives_number').val('');
        $('div#div_id_youth_lead_initiatives_number').addClass('d-none');
        $('#id_youth_lead_initiatives_number').removeClass('error-field');
    }
  }

