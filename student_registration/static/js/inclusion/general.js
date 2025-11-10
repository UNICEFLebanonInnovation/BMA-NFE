
$(document).ready(function() {

handleFormSubmit("#submit-id-save");
handleFormSubmit("#submit-id-save_add_another");

});

function handleFormSubmit(buttonSelector) {
    $(buttonSelector).click(function (e) {
        var form = $(this).closest("form")[0];

        if (form.checkValidity()) {
            $(this).prop('disabled', true);
            form.submit();
        } else {
            form.reportValidity();
            e.preventDefault();
        }
    });
}

