
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

    reorganizeForm();

     $(document).on('change', 'select#id_mid_test_done ', function(){
           reorganizeForm();
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


});


function reorganizeForm()
{
    var mid_test_done = $('select#id_mid_test_done').val();
    $('div.grades').addClass('d-none');
    if(mid_test_done == 'no')
    {
        $('#id_arabic_alphabet_knowledge').val('');
        $('#id_arabic_familiar_words').val('');
        $('#id_arabic_alphabet_knowledge').val('');

        $('#id_english_alphabet_knowledge').val('');
        $('#id_english_familiar_words').val('');
        $('#id_english_reading_comprehension').val('');

        $('#id_french_alphabet_knowledge').val('');
        $('#id_french_familiar_words').val('');
        $('#id_french_reading_comprehension').val('');

        $('#id_math').val('');
    }
    else
    {
        $('div.grades').removeClass('d-none');
        var language  = $('select#id_language').val();
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

}
