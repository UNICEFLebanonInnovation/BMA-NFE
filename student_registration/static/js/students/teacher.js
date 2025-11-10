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

    organize_form();
    if($(document).find('#id_academic_year_start').length == 1) {
        $('#id_academic_year_start').datepicker({dateFormat: "yy-mm-dd"});
    }
     if($(document).find('#id_academic_year_end').length == 1) {
        $('#id_academic_year_end').datepicker({dateFormat: "yy-mm-dd"});
    }

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

    $(document).on('change', 'select#id_extra_coaching, select#id_teacher_assignment', function () {
        organize_form();
    });

});



function organize_form() {
    extra_coaching = $('#id_extra_coaching').val();
    if (extra_coaching == 'yes') {
        $('#div_id_extra_coaching_specify').removeClass('d-none');
        $('#span_extra_coaching_specify').removeClass('d-none');
    }
    else
     {
        $('#span_extra_coaching_specify').addClass('d-none');
        $('#id_extra_coaching_specify').val('');
        $('#div_id_extra_coaching_specify').addClass('d-none');
    }

    teacher_assignment = $('#id_teacher_assignment').val();
    if (teacher_assignment == 'Private and Dirasa') {
        $('#div_id_teaching_hours_private_school').removeClass('d-none');
        $('#span_teaching_hours_private_school').removeClass('d-none');

        $('#div_id_teaching_hours_dirasa').removeClass('d-none');
        $('#span_teaching_hours_dirasa').removeClass('d-none');
    }
    else
     {
        $('#span_teaching_hours_private_school').addClass('d-none');
        $('#id_teaching_hours_private_school').val('');
        $('#div_id_teaching_hours_private_school').addClass('d-none');


        $('#span_teaching_hours_dirasa').addClass('d-none');
        $('#id_teaching_hours_dirasa').val('');
        $('#div_id_teaching_hours_dirasa').addClass('d-none');
    }
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


