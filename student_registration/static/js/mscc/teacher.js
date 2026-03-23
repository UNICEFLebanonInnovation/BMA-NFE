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
    if($(document).find('#id_birthdate').length == 1) {
        $('#id_birthdate').datepicker({dateFormat: "yy-mm-dd"}).attr("placeholder", "YYYY-MM-DD");
    }

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

        $('#div_id_teaching_hours_mscc').removeClass('d-none');
        $('#span_teaching_hours_mscc').removeClass('d-none');
    }
    else
     {
        $('#span_teaching_hours_private_school').addClass('d-none');
        $('#id_teaching_hours_private_school').val('');
        $('#div_id_teaching_hours_private_school').addClass('d-none');


        $('#span_teaching_hours_mscc').addClass('d-none');
        $('#id_teaching_hours_mscc').val('');
        $('#div_id_teaching_hours_mscc').addClass('d-none');
    }
}

function window_location(value)
{
    $('head').append('<meta http-equiv="refresh" content="0; URL='+value+'" id="redirect"/>');
}
