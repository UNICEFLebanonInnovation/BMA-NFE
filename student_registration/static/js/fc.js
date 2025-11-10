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

$(document).ready(function () {
    //Name and type added to page title
    var fc_type = $('#id_fc_type').val();
    document.title = "CLM | FC" + '-' + fc_type.toUpperCase();
//
//    if (isAddPage() ) {
//        $('#id_subject_taught').val(fc_type);
//    }

    if ($(document).find('#id_date_of_monitoring').length == 1) {
        $('#id_date_of_monitoring').datepicker({dateFormat: "yy-mm-dd"});
    }
    reorganizeForm();
    activities_reported();
    meet_objectives_verified();

    $(document).on('change', 'select#id_attend_lesson, ' +
        'select#id_child_acquire_competency, ' +
        'select#id_share_expectations, ' +
        'select#id_steps_acquire_competency, ' +
        'select#id_meet_objectives_verified, ' +
        'select#id_action_to_taken, ' +
        'select#id_sessions_participated, ' +
        'select#id_share_expectations_no_reason ', function(){
                reorganizeForm();
    });

    $(document).on('click', 'input[name=activities_reported]', function () {
        activities_reported();
    });
    $(document).on('click', 'input[name=meet_objectives_verified]', function () {
        meet_objectives_verified();
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

function isAddPage()
{
    var url_loc = window.location.toString();
    return (url_loc.toLowerCase().search(/^.*\/clm\/bln-fc-add|abln-fc-add|cbece-fc-add|rs-fc-add(\*)(\?.*)?$/i)>=0);
}

function pageScripts() {
    /* Magnific Popup */
    $('.image-link').magnificPopup({
        type: 'image',
        gallery: {
            enabled: true
        }
    });

}

function reorganizeForm()
{

    var sessions_participated = $('select#id_sessions_participated').val();
    if(sessions_participated == 'not_participating_at_all'){
        $('#div_id_not_participating_reason').removeClass('d-none');
        $('#span_not_participating_reason').removeClass('d-none');
    }
    else
    {
        $('#div_id_not_participating_reason').addClass('d-none');
        $('#span_not_participating_reason').addClass('d-none');
        $('#id_not_participating_reason').val('');
    }


    var action_to_taken = $('select#id_action_to_taken').val();
    if(action_to_taken == 'yes'){
        $('#div_id_action_to_taken_specify').removeClass('d-none');
        $('#span_action_to_taken_specify').removeClass('d-none');
    }
    else
    {
        $('#div_id_action_to_taken_specify').addClass('d-none');
        $('#span_action_to_taken_specify').addClass('d-none');
        $('#id_action_to_taken_specify').val('');

    }

    var meet_objectives_verified = $('select#id_meet_objectives_verified').val();

    if(meet_objectives_verified == 'other'){
        $('#div_id_objectives_verified_specify').removeClass('d-none');
        $('#span_objectives_verified_specify').removeClass('d-none');
    }
    else
    {
        $('#div_id_objectives_verified_specify').addClass('d-none');
        $('#span_objectives_verified_specify').addClass('d-none');
        $('#id_objectives_verified_specify').val('');

    }

    var share_expectations = $('select#id_share_expectations').val();
    var share_expectations_no_reason = $('select#id_share_expectations_no_reason').val();


    if (share_expectations == 'no') {
        $('#div_id_share_expectations_no_reason').removeClass('d-none');
        $('#span_share_expectations_no_reason').removeClass('d-none');
    }
    else {
        $('select#id_share_expectations_no_reason').val('');
        $('#id_share_expectations_other_reason').val('');
        $('#div_id_share_expectations_other_reason').addClass('d-none');
        $('#span_share_expectations_other_reason').addClass('d-none');
        $('#div_id_share_expectations_no_reason').addClass('d-none');
        $('#span_share_expectations_no_reason').addClass('d-none');

    }

    if(share_expectations_no_reason == 'other'){
        $('#div_id_share_expectations_other_reason').removeClass('d-none');
        $('#span_share_expectations_other_reason').removeClass('d-none');
    }
    else
    {
        $('#div_id_share_expectations_other_reason').addClass('d-none');
        $('#span_share_expectations_other_reason').addClass('d-none');
        $('#id_share_expectations_other_reason').val('');

    }
    var attend_lesson = $('select#id_attend_lesson').val();
    $('div.attend_lesson_questions').addClass('d-none');
    $('#attend_lesson_questions').addClass('hide');
    $('div#div_id_completed_tasks').removeClass('d-none');
    $('#span_completed_tasks').removeClass('d-none');
    $('div.steps_acquire_competency_questions').addClass('d-none');
    $('#steps_acquire_competency_questions').addClass('hide');


    if (attend_lesson == 'yes') {
        $('div#div_id_completed_tasks').addClass('d-none');
        $('#span_completed_tasks').addClass('d-none');
        $('div.attend_lesson_questions').removeClass('d-none');
        $('#attend_lesson_questions').removeClass('hide');
        var child_acquire_competency = $('select#id_child_acquire_competency').val();
        if (child_acquire_competency == 'no') {
            $('div.steps_acquire_competency_questions').removeClass('d-none');
            $('#steps_acquire_competency_questions').removeClass('hide');
        }
        else if (child_acquire_competency == 'yes')  {
            $('div.steps_acquire_competency_questions').addClass('d-none');
            $('#steps_acquire_competency_questions').addClass('hide');
        }

        var steps_acquire_competency= $('select#id_steps_acquire_competency').val();
        if(steps_acquire_competency == 'other'){
            $('#div_id_steps_acquire_competency_other').removeClass('d-none');
            $('#span_steps_acquire_competency_other').removeClass('d-none');
        }
        else
        {
            $('#div_id_steps_acquire_competency_other').addClass('d-none');
            $('#span_steps_acquire_competency_other').addClass('d-none');
            $('#id_steps_acquire_competency_other').val('');
        }
    }
    else {
        $('div.steps_acquire_competency_questions').addClass('d-none');
        $('#steps_acquire_competency_questions').addClass('hide');
        $('select#child_interact_teacher').val("no");
        $('select#child_interact_friends').val("no");
        $('select#child_clear_responses').val("no");
        $('select#child_ask_questions').val("no");
        $('select#child_show_improvement').val("no");
        $('#id_child_acquire_competency').val('');
        $('#id_steps_acquire_competency').val('');
        $('#id_steps_acquire_competency_other').val('');
    }
}

function activities_reported()
{
    var how_contact_caregivers = $('input[id=id_activities_reported_6]:checked').val();

    if (how_contact_caregivers == 'other') {
        $('div#div_id_activities_reported_other').removeClass('d-none');
        $('#span_activities_reported_other').removeClass('d-none');
    }
    else
    {
        $('div#div_id_activities_reported_other').addClass('d-none');
        $('#span_activities_reported_other').addClass('d-none');
        $('#id_activities_reported_other').val('');
    }
}


function meet_objectives_verified()
{
    var meet_objectives_verified = $('input[id=id_meet_objectives_verified_4]:checked').val();


    if (meet_objectives_verified == 'other') {
        $('div#div_id_objectives_verified_specify').removeClass('d-none');
        $('#span_objectives_verified_specify').removeClass('d-none');
    }
    else
    {
        $('div#div_id_objectives_verified_specify').addClass('d-none');
        $('#span_objectives_verified_specify').addClass('d-none');
        $('#id_objectives_verified_specify').val('');
    }
}
