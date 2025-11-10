
$(document).ready(function() {
    $("#submit-id-save").click(function(e){
        var form = $(this).closest('form')[0];
        var valid = form.checkValidity();

        if (typeof validateMainForm === 'function') {
            valid = validateMainForm(true) && valid;
        }

        if (valid) {
            $(this).prop('disabled', true);
            form.submit();
        } else {
            if (typeof form.reportValidity === 'function') {
                form.reportValidity();
            }
            e.preventDefault();
        }
    });

    $(document).on('click', '#next-page', function(e){
        e.preventDefault();
        $(this).removeClass('error-field');
        var error_fields = false;
        $('input, select').filter('[required]:visible').each(function(){
            if($(this).val() == null || $(this).val() == ''){
                $(this).addClass('error-field');
                error_fields = true;
            }
        });
        if(typeof validateMainForm === 'function' && !validateMainForm(false, 1)){
            error_fields = true;
        }
        if(!error_fields){
            $('#next-btn22').trigger('click');
            $(this).removeClass('error-field');
         }else{
            $('#formErrorModal').modal('show');
         }
    });

    // Handle forms where the visible "Next" button uses the id "next-btn22" directly
    // instead of the generic "next-page" id. Apply the same validation logic when
    // the button is clicked and only allow progressing if validation succeeds.
    $(document).on('click', '#next-btn22', function(e){
        $(this).removeClass('error-field');
        var error_fields = false;
        $('input, select').filter('[required]:visible').each(function(){
            if($(this).val() == null || $(this).val() == ''){
                $(this).addClass('error-field');
                error_fields = true;
            }
        });
        if(typeof validateMainForm === 'function' && !validateMainForm(false, 1)){
            error_fields = true;
        }
        if(error_fields){
            e.preventDefault();
            $('#formErrorModal').modal('show');
        }
    });
});

