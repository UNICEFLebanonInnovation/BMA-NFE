$(document).ready(function () {
    $('.image-link').each(function () {
        $('<img>').attr('src', $(this).attr('href')).appendTo('#image-cache');
    });

    if ($('#id_dropout_date').length) {
        $('#id_dropout_date').datepicker({ dateFormat: "yy-mm-dd" });
    }

    learning_result_next_level();
    reorganizeForm_post_assessment();

    // Event listeners for form changes
    const selectors = [
        '#id_participation', '#id_community_Liaison_follow_up', '#id_attended_arabic',
        '#id_attended_english', '#id_attended_math', '#id_attended_social', '#id_attended_psychomotor',
        '#id_attended_science', '#id_attended_artistic', '#id_parent_attended', '#id_pss_parent_attended',
        '#id_covid_parent_attended', '#id_followup_parent_attended', '#id_attended_biology',
        '#id_attended_chemistry', '#id_attended_physics', '#id_barriers_single', '#id_test_done',
        '#id_pss_session_attended', '#id_learning_result', '#id_covid_session_attended',
        '#id_followup_session_attended', '#id_referal_other', '#id_parent_attended_visits'
    ].join(',');

    $(document).on('change', selectors, reorganizeForm_post_assessment);

    $(document).on('click', '.delete-button', function () {
        if (confirm($(this).attr('translation'))) {
            const item = $(this);
            delete_student(item, () => item.closest('tr').remove());
        }
    });

    $(document).on('click', '.cancel-button', function (e) {
        e.preventDefault();
        if (confirm($(this).attr('translation'))) {
            window_location($(this).attr('href'));
        }
    });
});



function learning_result_next_level() {
    var registration_level = $('select#id_registration_level').val();
    var clm_type = $('#id_clmtype').val();
    if(clm_type=='ABLN' && registration_level=='level_two')
    {
        $("#id_learning_result option[value=" + 'graduated_to_abln_next_round_higher_level' + "]").hide();
    }
    else if(clm_type=='BLN' && registration_level=='level_three')
    {
        $("#id_learning_result option[value=" + 'graduated_to_bln_next_round_higher_level' + "]").hide();
    }
    else if(clm_type=='CBECE' && registration_level=='level_three')
    {
        $("#id_learning_result option[value=" + 'graduated_to_cbece_next_round_higher_level' + "]").hide();
    }
    else if(clm_type=='RS' && registration_level=='level_three')
    {
        $("#id_learning_result option[value=" + 'graduated_to_rs_next_round_higher_level' + "]").hide();
    }
}
function reorganizeForm_post_assessment()
{
   var learning_result =  $('select#id_learning_result').val();

    $('#span_learning_result_other').addClass('d-none');
    $('#div_id_learning_result_other').addClass('d-none');
    if(learning_result == 'other'){
        $('#span_learning_result_other').removeClass('d-none');
        $('#div_id_learning_result_other').removeClass('d-none');
    }

    $('#div_id_dropout_reason').addClass('d-none');
    $('#span_dropout_reason').addClass('d-none');
    $('#div_id_dropout_date').addClass('d-none');
    $('#span_dropout_date').addClass('d-none');
    if(learning_result == 'dropout'){
        $('#div_id_dropout_reason').removeClass('d-none');
        $('#span_dropout_reason').removeClass('d-none');
        $('#div_id_dropout_date').removeClass('d-none');
        $('#span_dropout_date').removeClass('d-none');
    }

    $('div#div_id_referral_school').addClass('d-none');
    $('#span_referral_school').addClass('d-none');
    $('div#div_id_referral_school_type').addClass('d-none');
    $('#span_referral_school_type').addClass('d-none');
    if(learning_result == 'referred_public_school'){
        $('div#div_id_referral_school').removeClass('d-none');
        $('#span_referral_school').removeClass('d-none');
        $('div#div_id_referral_school_type').removeClass('d-none');
        $('#span_referral_school_type').removeClass('d-none');
    }

    var participation = $('select#id_participation').val();
    var barriers_single = $('select#id_barriers_single').val();
    var test_done = $('select#id_test_done').val();
    var language  = $('select#id_language').val();

    var community_Liaison_follow_up = $('select#id_community_Liaison_follow_up').val();

    var pss_session_attended = $('select#id_pss_session_attended').val();
    var covid_session_attended = $('select#id_covid_session_attended').val();
    var followup_session_attended = $('select#id_followup_session_attended').val();

    var pss_parent_attended =  $('select#id_pss_parent_attended').val();
    var covid_parent_attended =  $('select#id_covid_parent_attended').val();
    var followup_parent_attended =  $('select#id_followup_parent_attended').val();

    var parent_attended_visits = $('select#id_parent_attended_visits').val();
    var grade_registration = $('select#id_grade_registration').val();

    var referal_other = $('select#id_referal_other').val();

    // id_participation
    $('div#div_id_barriers_single').addClass('d-none');
    $('#span_barriers_single').addClass('d-none');
    $('div#div_id_barriers_other').addClass('d-none');
    $('#span_barriers_other').addClass('d-none');
    $('#div_id_community_Liaison_follow_up').removeClass('d-none');
    $('#span_community_Liaison_follow_up').removeClass('d-none');

    if(participation != 'no_absence'){
        $('#div_id_barriers_single').removeClass('d-none');
        $('#span_barriers_single').removeClass('d-none');
        if (barriers_single =='other'){
            $('div#div_id_barriers_other').removeClass('d-none');
            $('#span_barriers_other').removeClass('d-none');
        }
        $('#div_id_community_Liaison_follow_up').removeClass('d-none');
        $('#span_community_Liaison_follow_up').removeClass('d-none');
    }
    else{
        $('#div_id_barriers_single').addClass('d-none');
        $('#span_barriers_single').addClass('d-none');
        $('div#div_id_barriers_other').addClass('d-none');
        $('#span_barriers_other').addClass('d-none');
        $('#div_id_community_Liaison_follow_up').addClass('d-none');
        $('#span_community_Liaison_follow_up').addClass('d-none');
        $('#span_community_liaison_specify').addClass('d-none');
        $('div#div_id_community_liaison_specify').addClass('d-none');
    }

    $('#span_community_liaison_specify').addClass('d-none');
    $('div#div_id_community_liaison_specify').addClass('d-none');
    if(community_Liaison_follow_up == 'yes'){
        $('#div_id_community_liaison_specify').removeClass('d-none');
        $('#span_community_liaison_specify').removeClass('d-none');
    }
    else
    {
        $('#span_community_liaison_specify').addClass('d-none');
        $('div#div_id_community_liaison_specify').addClass('d-none');
    }

    $('div#div_id_round_complete').addClass('d-none');
    $('#span_round_complete').addClass('d-none');

    if(test_done == 'yes'){
    $('#div_id_round_complete').removeClass('d-none');
    $('#span_round_complete').removeClass('d-none');
    $('#grades').removeClass('hide');
    $('div.grades').removeClass('d-none');

    //    id_language
    if (language == 'english_arabic')
    {
        $('#div_id_english_alphabet_knowledge').removeClass('d-none');
        $('#div_id_english_familiar_words').removeClass('d-none');
        $('#div_id_english_reading_comprehension').removeClass('d-none');
        $('#span_english').removeClass('d-none');
    }
    else
    {
        $('#div_id_english_alphabet_knowledge').addClass('d-none');
        $('#div_id_english_familiar_words').addClass('d-none');
        $('#div_id_english_reading_comprehension').addClass('d-none');
        $('#span_english').addClass('d-none');
    }
    if (language == 'french_arabic')
    {
        $('#div_id_french_alphabet_knowledge').removeClass('d-none');
        $('#div_id_french_familiar_words').removeClass('d-none');
        $('#div_id_french_reading_comprehension').removeClass('d-none');
        $('#span_french').removeClass('d-none');
    }
    else
    {
        $('#div_id_french_alphabet_knowledge').addClass('d-none');
        $('#div_id_french_familiar_words').addClass('d-none');
        $('#div_id_french_reading_comprehension').addClass('d-none');
        $('#span_french').addClass('d-none');
    }
    }
    else
    {
        $('select#id_round_complete').val("");

        // grades

        $('#id_arabic_alphabet_knowledge').val('');
        $('#id_arabic_familiar_words').val('');
        $('#id_arabic_reading_comprehension').val('');
        $('#id_english_alphabet_knowledge').val('');
        $('#id_english_familiar_words').val('');
        $('#id_english_reading_comprehension').val('');
        $('#id_french_alphabet_knowledge').val('');
        $('#id_french_familiar_words').val('');
        $('#id_french_reading_comprehension').val('');
        $('#id_math').val('');

        $('div.grades').addClass('d-none');
        $('#grades').addClass('hide');
    }

    learning_result_next_level();

    // grade_registration
    $('div.grd6').addClass('d-none');
    $('#grd6').addClass('hide');
    $('div.grd7').addClass('d-none');
    $('#grd7').addClass('hide');


     if (grade_registration == '7' || grade_registration == '8' || grade_registration == '9') {
        $('div.grd6').addClass('d-none');
        $('#grd6').addClass('hide');
        $('div.grd7').removeClass('d-none');
        $('#grd7').removeClass('hide');
        $('#id_science').val('');
        $('select#id_attended_science').val("no");
        $('select#id_modality_science').val("");
    }
    else {
        $('#grd6').removeClass('hide');
        $('div.grd6').removeClass('d-none');
        $('#grd7').addClass('hide');
        $('div.grd7').addClass('d-none');
        $('#id_biology').val('');
        $('select#id_attended_biology').val("no");
        $('select#id_modality_biology').val("");

        $('#id_chemistry').val('');
        $('select#id_attended_chemistry').val("no");
        $('select#id_modality_chemistry').val("");

        $('#id_physics').val('');
        $('select#id_attended_physics').val("no");
        $('select#id_modality_physics').val("");
    }
}
