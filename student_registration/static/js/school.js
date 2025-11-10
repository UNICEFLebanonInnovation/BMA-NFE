/**
 * Created by yosr on 05/31/22.
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

$(document).ready(function() {

        reorganizeForm();

    if($(document).find('#id_academic_year_start').length == 1) {
        $('#id_academic_year_start').datepicker({dateFormat: "yy-mm-dd"});
    }
     if($(document).find('#id_academic_year_end').length == 1) {
        $('#id_academic_year_end').datepicker({dateFormat: "yy-mm-dd"});
    }

     if($(document).find('#id_meeting_date').length == 1) {
        $('#id_meeting_date').datepicker({dateFormat: "yy-mm-dd"});
    }

     if($(document).find('#id_date_first_visit').length == 1) {
        $('#id_date_first_visit').datepicker({dateFormat: "yy-mm-dd"});
    }

     if($(document).find('#id_date_last_visit').length == 1) {
        $('#id_date_last_visit').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', 'select#id_benefit_wfp_service', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_digital_learning_programme', function(){
        reorganizeForm();
    });

    $(document).on('click', '.justify-button', function(){
        var item = $(this);
        var itemscope = item.attr('itemscope');
        if(confirm($(this).attr('translation'))) {
            $('.justify-date-block').addClass('d-none');
            $('#justify_date_block_'+itemscope).removeClass('d-none');
            var itemscope = item.attr('itemscope');
            justify_student_enrollment(item.attr('itemscope'));
        }
    });

    $(document).on('click', '.cancel-button', function(e){
        e.preventDefault();
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            window_location(item.attr('href'));
        }
    });

    pageScripts();

    /* Ajax page load settings */
    $(document).on('pjax:end', pageScripts);
    if (sessionStorage.getItem("pjax-enabled") === "0") {
        return;
    }
    // Comment it to disable Ajax Page load
    //$(document).pjax('a', '.content-wrap', {fragment: '.content-wrap'});

    $(document).on('pjax:beforeReplace', function() {
        $('.content-wrap').css('opacity', '0.1');
        setTimeout(function() {
            $('.content-wrap').fadeTo('100', '1');
        }, 1);
    });
});

function reorganizeForm()
{
    var benefit_wfp_service = $('select#id_benefit_wfp_service').val();

     // wfp_service_type
    $('div#div_id_wfp_service_type').addClass('d-none');
    $('#span_wfp_service_type').addClass('d-none');


    if(benefit_wfp_service == 'yes'){
        $('#div_id_wfp_service_type').removeClass('d-none');
        $('#span_wfp_service_type').removeClass('d-none');
    }

    var digital_learning_programme = $('select#id_digital_learning_programme').val();

     // wfp_service_type
    $('div#div_id_school_digital_capacity').addClass('d-none');
    $('#span_school_digital_capacity').addClass('d-none');


    if(digital_learning_programme == 'yes'){
        $('#div_id_school_digital_capacity').removeClass('d-none');
        $('#span_school_digital_capacity').removeClass('d-none');
    }
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

function urlParam(name){
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	if (results && results.length){
        return results[1] || 0;
    }
    return 0;
}

function window_location(value)
{
    console.log('OK');
    $('head').append('<meta http-equiv="refresh" content="0; URL='+value+'" id="redirect"/>');
}

function load_districts(url)
{
    var value = $("#id_governorate").val();
    $.ajax({
        url: url,
        data: {
            'id_governorate': value
        },
        success: function (data) {
            $("#id_district").html(data);
        }
    })
}

function load_cadasters(url)
{
    var value = $("#id_district").val();
    $.ajax({
        url: url,
        data: {
            'id_district': value
        },
        success: function (data) {
            $("#id_cadaster").html(data);
        }
    })
}

function load_schools(url)
{
    var value = $("#id_governorate").val();
    $.ajax({
        url: url,
        data: {
            'id_governorate': value
        },
        success: function (data) {
            $("#id_school").html(data);
        }
    })
}

