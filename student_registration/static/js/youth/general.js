
$(document).ready(function() {
    $("#submit-id-save").click(function(e){
        $(this).prop('disabled', true);
        $('form').submit();
    });
});

