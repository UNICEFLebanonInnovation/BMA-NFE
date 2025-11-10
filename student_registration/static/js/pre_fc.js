/**
 * Created by yosr on 11/26/20.
 */

var protocol = window.location.protocol;
var host = protocol+window.location.host;

$(window).load(function () {

    /* Background loading full-size images */
    $('.image-link').each(function() {
        var src = $(this).attr('href');
        var img = document.createElement('img');

        img.src = src;
        $('#image-cache').append(img);
    });

});

$(document).ready(function(){

    reorganizeForm_post_assessment();


    $(document).on('change', 'select#id_participation,  select#id_attended_arabic, select#id_attended_english,  select#id_attended_math,  ' +
        'select#id_attended_social,  select#id_attended_psychomotor ,  select#id_attended_science ,  select#id_attended_artistic , select#id_parent_attended ,' +
        'select#id_pss_parent_attended,  select#id_covid_parent_attended ,  select#id_followup_parent_attended ,' +
        'select#id_attended_biology,  select#id_attended_chemistry ,  select#id_attended_physics ,' +
        'select#id_barriers_single,  select#id_test_done ,  select#id_pss_session_attended , select#id_learning_result , ' +
        'select#id_covid_session_attended,  select#id_followup_session_attended ,  select#id_parent_attended_visits ', function(){
       reorganizeForm_post_assessment();
    });

    $(document).on('click', '.delete-button', function(){
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            var callback = function(){
                item.parents('tr').remove();
            };
            delete_student(item, callback());
        }
    });

    $(document).on('click', '.cancel-button', function(e){
        e.preventDefault();
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            window_location(item.attr('href'));
//            window.location = item.attr('href');
        }
    });

    pageScripts();

        /* Ajax page load settings */
        $(document).on('pjax:end', pageScripts);
        if (sessionStorage.getItem("pjax-enabled") === "0") {
            return;
        }

        // Comment it to disable Ajax Page load
        $(document).pjax('a', '.content-wrap', {fragment: '.content-wrap'});

        $(document).on('pjax:beforeReplace', function() {
            $('.content-wrap').css('opacity', '0.1');
            setTimeout(function() {
                $('.content-wrap').fadeTo('100', '1');
            }, 1);
        });
});

function pageScripts() {
    /* Magnific Popup */
    $('.image-link').magnificPopup({
        type: 'image',
        gallery: {
            enabled: true
        }
    });
}

function reorganizeForm_post_assessment()
{

    var participation = $('select#id_participation').val();
    var barriers_single = $('select#id_barriers_single').val();
    var test_done = $('select#id_test_done').val();
    // var follow_up_type = $('select#id_follow_up_type').val();

    var attended_arabic = $('select#id_attended_arabic').val();
    var attended_english = $('select#id_attended_english').val();
    var attended_math = $('select#id_attended_math').val();
    var attended_social = $('select#id_attended_social').val();
    var attended_psychomotor = $('select#id_attended_psychomotor').val();

    var attended_science = $('select#id_attended_science').val();
    var attended_artistic = $('select#id_attended_artistic').val();

    var attended_biology = $('select#id_attended_biology').val();
    var attended_chemistry = $('select#id_attended_chemistry').val();
    var attended_physics = $('select#id_attended_physics').val();

    var pss_session_attended = $('select#id_pss_session_attended').val();
    var covid_session_attended = $('select#id_covid_session_attended').val();
    var followup_session_attended = $('select#id_followup_session_attended').val();

    var pss_parent_attended =  $('select#id_pss_parent_attended').val();
    var covid_parent_attended =  $('select#id_covid_parent_attended').val();
    var followup_parent_attended =  $('select#id_followup_parent_attended').val();

    var parent_attended_visits = $('select#id_parent_attended_visits').val();
    var grade_registration = $('select#id_grade_registration').val();

    var learning_result = $('select#id_learning_result').val();


    // id_participation
    $('div#div_id_barriers_single').addClass('d-none');
    $('#span_barriers_single').addClass('d-none');
    $('div#div_id_barriers_other').addClass('d-none');
    $('#span_barriers_other').addClass('d-none');
    // $('#follow_up').addClass('hide');
    // $('#visits').addClass('hide');



    if(participation != 'no_absence'){
        $('#div_id_barriers_single').removeClass('d-none');
        $('#span_barriers_single').removeClass('d-none');
        // $('#follow_up').removeClass('hide');
        // $('#visits').removeClass('hide');
        // $('input[name=follow_up_type]').val('none').checked(true);
        // $('#id_phone_call_number').val('');
        // $('#id_house_visit_number').val('');
        // $('#id_family_visit_number').val('');
    }

    if(barriers_single == 'other'){
        $('#div_id_barriers_other').removeClass('d-none');
        $('#span_barriers_other').removeClass('d-none');
    }
    else
    {
        $('#id_barriers_other').val('');
    }

    // learning_result
    $('div#div_id_learning_result_other').addClass('d-none');
    $('#span_learning_result_other').addClass('d-none');
    if(learning_result == 'other'){
        $('#div_id_learning_result_other').removeClass('d-none');
        $('#span_learning_result_other').removeClass('d-none');
    }
    // else
    // {
    //     $('#id_learning_result_other').val('');
    // }

    $('div#div_id_round_complete').addClass('d-none');
    $('#span_round_complete').addClass('d-none');
    $('div.grades').addClass('d-none');
    $('#grades').addClass('hide');

    if(test_done == 'yes'){
    $('#div_id_round_complete').removeClass('d-none');
    $('#span_round_complete').removeClass('d-none');
    $('#grades').removeClass('hide');
    $('div.grades').removeClass('d-none');

    }
    else
    {
        $('select#id_round_complete').val("");

        // grades
        $('#id_arabic').val('');
        $('select#id_attended_arabic').val("no");
        $('select#id_modality_arabic').val("");
        $('#id_english').val('');
        $('select#id_attended_english').val("no");
        $('select#id_modality_english').val("");
        $('#id_math').val('');
        $('select#id_attended_math').val("no");
        $('select#id_modality_math').val("");
        $('#id_social').val('');
        $('select#id_attended_social').val("no");
        $('select#id_modality_social').val("");
        $('#id_psychomotor').val('');
        $('select#id_attended_psychomotor').val("no");
        $('select#id_modality_psychomotor').val("");
        $('#id_science').val('');
        $('select#id_attended_science').val("no");
        $('select#id_modality_science').val("");
        $('#id_artistic').val('');
        $('select#id_attended_artistic').val("no");
        $('select#id_modality_artistic').val("");


        $('#id_biology').val('');
        $('select#id_attended_biology').val("no");
        $('select#id_modality_biology').val("");

        $('#id_chemistry').val('');
        $('select#id_attended_chemistry').val("no");
        $('select#id_modality_chemistry').val("");

        $('#id_physics').val('');
        $('select#id_attended_physics').val("no");
        $('select#id_modality_physics').val("");

        $('div.grades').addClass('d-none');
        $('#grades').addClass('hide');
    }

    // grade_registration
    $('div.grd6').addClass('d-none');
    $('#grd6').addClass('hide');
    $('div.grd7').addClass('d-none');
    $('#grd7').addClass('hide');
    if(grade_registration == '6'){
        $('#grd6').removeClass('hide');
        $('div.grd6').removeClass('d-none');
    }
    else
    {
        $('div.grd6').addClass('d-none');
        $('#grd6').addClass('hide');
    }

    if(grade_registration == '7' || grade_registration == '8' || grade_registration == '9'){
        $('#grd7').removeClass('hide');
        $('div.grd7').removeClass('d-none');
    }
    else
    {
        $('div.grd7').addClass('d-none');
        $('#grd7').addClass('hide');
    }


    // // follow_up_type
    // $('div#div_phone_call_number').addClass('d-none');
    // $('div#div_house_visit_number').addClass('d-none');
    // $('div#div_family_visit_number').addClass('d-none');
    // if(follow_up_type == 'Phone'){
    //     $('div#div_phone_call_number').removeClass('d-none');
    //
    // }else if(follow_up_type == 'House visit'){
    //     $('div#div_house_visit_number').removeClass('d-none');
    //
    // }else if(follow_up_type == 'Family Visit') {
    //     $('div#div_family_visit_number').removeClass('d-none');
    // }

    $('div#div_id_arabic').addClass('d-none');
    $('#span_arabic').addClass('d-none');
    $('div#div_id_modality_arabic').addClass('d-none');
    $('#span_modality_arabic').addClass('d-none');

    $('div#div_id_english').addClass('d-none');
    $('#span_english').addClass('d-none');
    $('div#div_id_modality_english').addClass('d-none');
    $('#span_modality_english').addClass('d-none');

    $('div#div_id_math').addClass('d-none');
    $('#span_math').addClass('d-none');
    $('div#div_id_modality_math').addClass('d-none');
    $('#span_modality_math').addClass('d-none');

    $('div#div_id_social_emotional').addClass('d-none');
    $('#span_social_emotional').addClass('d-none');
    $('div#div_id_modality_social').addClass('d-none');
    $('#span_modality_social').addClass('d-none');

    $('div#div_id_psychomotor').addClass('d-none');
    $('#span_psychomotor').addClass('d-none');
    $('div#div_id_modality_psychomotor').addClass('d-none');
    $('#span_modality_psychomotor').addClass('d-none');


    $('div#div_id_science').addClass('d-none');
    $('#span_science').addClass('d-none');
    $('div#div_id_modality_science').addClass('d-none');
    $('#span_modality_science').addClass('d-none');

    $('div#div_id_artistic').addClass('d-none');
    $('#span_artistic').addClass('d-none');
    $('div#div_id_modality_artistic').addClass('d-none');
    $('#span_modality_artistic').addClass('d-none');

        // , , physics

    $('div#div_id_biology').addClass('d-none');
    $('#span_biology').addClass('d-none');
    $('div#div_id_modality_biology').addClass('d-none');
    $('#span_modality_biology').addClass('d-none');


    $('div#div_id_chemistry').addClass('d-none');
    $('#span_chemistry').addClass('d-none');
    $('div#div_id_modality_chemistry').addClass('d-none');
    $('#span_modality_chemistry').addClass('d-none');


    $('div#div_id_physics').addClass('d-none');
    $('#span_physics').addClass('d-none');
    $('div#div_id_modality_physics').addClass('d-none');
    $('#span_modality_physics').addClass('d-none');

    // attended_arabic
    if(attended_arabic == 'yes'){
        $('div#div_id_arabic').removeClass('d-none');
        $('#span_arabic').removeClass('d-none');
        $('div#div_id_modality_arabic').removeClass('d-none');
        $('#span_modality_arabic').removeClass('d-none');

    }
    else{
        $('#id_arabic').val('');
        $('select#id_modality_arabic').val("");

    }

    // attended_english
    if(attended_english == 'yes'){
        $('div#div_id_english').removeClass('d-none');
        $('#span_english').removeClass('d-none');
        $('div#div_id_modality_english').removeClass('d-none');
        $('#span_modality_english').removeClass('d-none');

    }
    else{
        $('#id_english').val('');
        $('select#id_modality_english').val("");
    }

    // attended_math
    if(attended_math == 'yes'){
        $('div#div_id_math').removeClass('d-none');
        $('#span_math').removeClass('d-none');
        $('div#div_id_modality_math').removeClass('d-none');
        $('#span_modality_math').removeClass('d-none');
    }
    else{
        $('#id_math').val('');
        $('select#id_modality_math').val("");
    }
    // attended_social
    if(attended_social == 'yes'){
        $('div#div_id_social_emotional').removeClass('d-none');
        $('#span_social_emotional').removeClass('d-none');
        $('div#div_id_modality_social').removeClass('d-none');
        $('#span_modality_social').removeClass('d-none');
    }
    else{
        $('#id_social').val('');
        $('select#id_modality_social').val("");
    }
    // attended_psychomotor
    if(attended_psychomotor == 'yes'){
        $('div#div_id_psychomotor').removeClass('d-none');
        $('#span_psychomotor').removeClass('d-none');
        $('div#div_id_modality_psychomotor').removeClass('d-none');
        $('#span_modality_psychomotor').removeClass('d-none');
    }
    else{
        $('#id_psychomotor').val('');
        $('select#id_modality_psychomotor').val("");
    }

    // attended_science,
    if(attended_science == 'yes'){
        $('div#div_id_science').removeClass('d-none');
        $('#span_science').removeClass('d-none');
        $('div#div_id_modality_science').removeClass('d-none');
        $('#span_modality_science').removeClass('d-none');
    }
    else{
        $('#id_science').val('');
        $('select#id_modality_science').val("");
    }

    // attended_artistic
    if(attended_artistic == 'yes'){
        $('div#div_id_artistic').removeClass('d-none');
        $('#span_artistic').removeClass('d-none');
        $('div#div_id_modality_artistic').removeClass('d-none');
        $('#span_modality_artistic').removeClass('d-none');
    }
    else{
        $('#id_artistic').val('');
        $('select#id_modality_artistic').val("");
    }


    // biology, chemistry, physics
    // attended_biology
    if(attended_biology == 'yes'){
        $('div#div_id_biology').removeClass('d-none');
        $('#span_biology').removeClass('d-none');
        $('div#div_id_modality_biology').removeClass('d-none');
        $('#span_modality_biology').removeClass('d-none');
    }
    else{
        $('#id_biology').val('');
        $('select#id_modality_biology').val("");
    }

    // attended_chemistry
    if(attended_chemistry == 'yes'){
        $('div#div_id_chemistry').removeClass('d-none');
        $('#span_chemistry').removeClass('d-none');
        $('div#div_id_modality_chemistry').removeClass('d-none');
        $('#span_modality_chemistry').removeClass('d-none');
    }
    else{
        $('#id_chemistry').val('');
        $('select#id_modality_chemistry').val("");
    }

    // attended_physics
    if(attended_physics == 'yes'){
        $('div#div_id_physics').removeClass('d-none');
        $('#span_physics').removeClass('d-none');
        $('div#div_id_modality_physics').removeClass('d-none');
        $('#span_modality_physics').removeClass('d-none');
    }
    else{
        $('#id_physics').val('');
        $('select#id_modality_physics').val("");
    }

    // pss_parent_attended
    $('#div_id_pss_parent_attended_other').addClass('d-none');
    $('#span_pss_parent_attended_other').addClass('d-none');
    if(pss_parent_attended == 'other'){
        $('#div_id_pss_parent_attended_other').removeClass('d-none');
        $('#span_pss_parent_attended_other').removeClass('d-none');
    }
    else
    {
        $('#id_pss_parent_attended_other').val('');
    }

    // pss_session_modality
    $('div#div_id_pss_session_number').addClass('d-none');
    $('#span_pss_session_number').addClass('d-none');
    $('div#div_id_pss_session_modality').addClass('d-none');
    $('#span_pss_session_modality').addClass('d-none');
    // $('div#div_id_pss_parent_attended_other').addClass('d-none');
    // $('#span_pss_parent_attended_other').addClass('d-none');
    $('div#div_id_pss_parent_attended').addClass('d-none');
    $('#span_pss_parent_attended').addClass('d-none');


    if(pss_session_attended == 'yes'){
        $('div#div_id_pss_session_number').removeClass('d-none');
        $('#span_pss_session_number').removeClass('d-none');
        $('div#div_id_pss_session_modality').removeClass('d-none');
        $('#span_pss_session_modality').removeClass('d-none');
        // $('div#div_id_pss_parent_attended_other').removeClass('d-none');
        // $('#span_pss_parent_attended_other').removeClass('d-none');
        $('div#div_id_pss_parent_attended').removeClass('d-none');
        $('#span_pss_parent_attended').removeClass('d-none');
    }
    else{
        $('#id_pss_session_number').val('');
        $('select#div_id_pss_session_modality').val("");
        $('#span_pss_parent_attended_other').val('');
        $('select#div_id_pss_parent_attended').val("");

    }

 // covid_parent_attended
    $('#div_id_covid_parent_attended_other').addClass('d-none');
    $('#span_covid_parent_attended_other').addClass('d-none');
    if(covid_parent_attended == 'other'){
        $('#div_id_covid_parent_attended_other').removeClass('d-none');
        $('#span_covid_parent_attended_other').removeClass('d-none');
    }
    else
    {
        $('#id_covid_parent_attended_other').val('');
    }

    // covid_session_modality
    $('div#div_id_covid_session_number').addClass('d-none');
    $('#span_covid_session_number').addClass('d-none');
    $('div#div_id_covid_session_modality').addClass('d-none');
    $('#span_covid_session_modality').addClass('d-none');
    // $('div#div_id_covid_parent_attended_other').addClass('d-none');
    // $('#span_covid_parent_attended_other').addClass('d-none');
    $('div#div_id_covid_parent_attended').addClass('d-none');
    $('#span_covid_parent_attended').addClass('d-none');


    if(covid_session_attended == 'yes'){
        $('div#div_id_covid_session_number').removeClass('d-none');
        $('#span_covid_session_number').removeClass('d-none');
        $('div#div_id_covid_session_modality').removeClass('d-none');
        $('#span_covid_session_modality').removeClass('d-none');
        // $('div#div_id_covid_parent_attended_other').removeClass('d-none');
        // $('#span_covid_parent_attended_other').removeClass('d-none');
        $('div#div_id_covid_parent_attended').removeClass('d-none');
        $('#span_covid_parent_attended').removeClass('d-none');
    }
    else{
        $('#id_covid_session_number').val('');
        $('select#div_id_covid_session_modality').val("");
        $('#span_covid_parent_attended_other').val('');
        $('select#div_id_covid_parent_attended').val("");
    }


     // followup_parent_attended
    $('#div_id_followup_parent_attended_other').addClass('d-none');
    $('#span_followup_parent_attended_other').addClass('d-none');
    if(followup_parent_attended == 'other'){
        $('#div_id_followup_parent_attended_other').removeClass('d-none');
        $('#span_followup_parent_attended_other').removeClass('d-none');
    }
    else
    {
        $('#id_followup_parent_attended_other').val('');
    }

    // followup_session_modality
    $('div#div_id_followup_session_number').addClass('d-none');
    $('#span_followup_session_number').addClass('d-none');
    $('div#div_id_followup_session_modality').addClass('d-none');
    $('#span_followup_session_modality').addClass('d-none');
    // $('div#div_id_followup_parent_attended_other').addClass('d-none');
    // $('#span_followup_parent_attended_other').addClass('d-none');
    $('div#div_id_followup_parent_attended').addClass('d-none');
    $('#span_followup_parent_attended').addClass('d-none');


    if(followup_session_attended == 'yes'){
        $('div#div_id_followup_session_number').removeClass('d-none');
        $('#span_followup_session_number').removeClass('d-none');
        $('div#div_id_followup_session_modality').removeClass('d-none');
        $('#span_followup_session_modality').removeClass('d-none');
        // $('div#div_id_followup_parent_attended_other').removeClass('d-none');
        // $('#span_followup_parent_attended_other').removeClass('d-none');
        $('div#div_id_followup_parent_attended').removeClass('d-none');
        $('#span_followup_parent_attended').removeClass('d-none');
    }
    else{
        $('#id_followup_session_number').val('');
        $('select#div_id_followup_session_modality').val("");
        $('#span_followup_parent_attended_other').val('');
        $('select#div_id_followup_parent_attended').val("");
    }

    $('div.parent_visits').addClass('d-none');
    $('#parent_visits').addClass('hide');

    if(parent_attended_visits == 'yes'){
    $('#parent_visits').removeClass('hide');
    $('div.parent_visits').removeClass('d-none');

    }
    else
    {
        $('#id_followup_session_number').val('');
        $('select#div_id_followup_session_modality').val("");
        $('#span_followup_parent_attended_other').val('');
        $('select#div_id_followup_parent_attended').val("");
        $('#id_covid_session_number').val('');
        $('select#div_id_covid_session_modality').val("");
        $('#span_covid_parent_attended_other').val('');
        $('select#div_id_covid_parent_attended').val("");
        $('#id_pss_session_number').val('');
        $('select#div_id_pss_session_modality').val("");
        $('#span_pss_parent_attended_other').val('');
        $('select#div_id_pss_parent_attended').val("");
        $('div.parent_visits').addClass('d-none');
        $('#parent_visits').addClass('hide');
    }



}
