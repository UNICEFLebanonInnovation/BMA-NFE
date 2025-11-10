/**
 * Created by yosr on 11/24/20.
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

    reorganizeForm_mid_assessment();

        $(document).on('change', 'select#id_attended_arabic, select#id_attended_english, select#id_attended_math,  select#id_attended_social,  ' +
        'select#id_attended_psychomotor, select#id_attended_science , select#id_attended_artistic,  select#id_mid_test_done ', function(){
       reorganizeForm_mid_assessment();
    });

    $(document).on('click', '.cancel-button', function(e){
        e.preventDefault();
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            window_location(item.attr('href'));
//            window.location = item.attr('href');
        }
    });

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


function reorganizeForm_mid_assessment()
{
    var mid_test_done = $('select#id_mid_test_done').val();

    var attended_arabic = $('select#id_attended_arabic').val();
    var attended_english = $('select#id_attended_english').val();
    var attended_math = $('select#id_attended_math').val();
    var attended_social = $('select#id_attended_social').val();
    var attended_psychomotor = $('select#id_attended_psychomotor').val();
    var attended_science = $('select#id_attended_science').val();
    var attended_artistic = $('select#id_attended_artistic').val();

    $('div.grades').addClass('d-none');
    if(mid_test_done == 'yes'){
    // $('#grades').removeClass('hide');
    $('div.grades').removeClass('d-none');
    }
    else
    {
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
    }

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

    $('div#div_id_artistic ').addClass('d-none');
    $('#span_artistic ').addClass('d-none');
    $('div#div_id_modality_artistic ').addClass('d-none');
    $('#span_modality_artistic ').addClass('d-none');

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

}



