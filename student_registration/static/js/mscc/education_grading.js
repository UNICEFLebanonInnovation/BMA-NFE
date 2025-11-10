

$(document).ready(function(){
       reorganizeForm();

    $(document).on('change', ' select#id_post_test_done' , function(){
       reorganizeForm();
    });


});


function reorganizeForm()
{
    var post_test_done = $('select#id_post_test_done').val();


    if(post_test_done == 'Yes'){
        $('.grade-field').removeClass('d-none');
    }else{
        $('.grade-field').addClass('d-none');
        $('.grade-field').find('input').val(0);
    }
}
