
function validatorMessage(message) {
    return window.gettext ? window.gettext(message) : message;
}

function checkArabicOnly(field)
{
    return checkFieldCharacters
    (
        field,
        function(ch)
        {
            var c = ch.charCodeAt(0);
            return !((c < 1536 || c > 1791) && ch != " ");
        },
        validatorMessage('Please use Arabic letters only.')
    );
}
function checkEnglishOnly(field) {
    return checkFieldCharacters(
        field,
        function(ch) {
            var c = ch.charCodeAt(0);
            return ((c >= 65 && c <= 90) ||    // A–Z
                    (c >= 97 && c <= 122) ||   // a–z
                    ch === " ");
        },
        validatorMessage('Please use English letters only.')
    );
}
function checkIsNumber(field)
{
    return checkFieldCharacters
    (
        field,
        function(ch)
        {
            return checkCharacterIsNumber(ch);
        },
        validatorMessage('Please use digits only.')
    );
}

/*
 * This used to silently delete every character that failed the check, so a name
 * typed in the wrong script vanished on blur with no explanation and no way to
 * get it back. Flag the field instead and leave what the user typed alone.
 */
function checkFieldCharacters(field, characterCheck, message)
{
    var sFieldVal = field.val() || "";
    var isValid = true;

    for(var i = 0; i < sFieldVal.length; i++) {
        if(!characterCheck(sFieldVal.charAt(i))) {
            isValid = false;
            break;
        }
    }

    markFieldCharacterError(field, isValid, message);
    return isValid;
}

function markFieldCharacterError(field, isValid, message)
{
    var feedbackId = (field.attr('id') || 'field') + '-charset-error';
    var $feedback = $('#' + feedbackId);

    if(isValid) {
        field.removeClass('is-invalid');
        field.removeAttr('aria-invalid');
        $feedback.remove();
        return;
    }

    field.addClass('is-invalid');
    field.attr('aria-invalid', 'true');

    if(!$feedback.length) {
        // Deliberately not `.invalid-feedback`: the forms' own validateField()
        // blanks every .invalid-feedback sibling it finds, which would wipe this
        // message straight back out again.
        $feedback = $('<div class="charset-feedback text-danger small mt-1"></div>').attr('id', feedbackId);
        field.after($feedback);
    }
    $feedback.text(message || validatorMessage('This value contains characters that are not allowed.'));
}

function checkCharacterIsNumber(fieldValue)
{
    return /^[0-9]+$/.test(fieldValue);
}
function check_unhcr_number(id_number)
{
    var patt = /^((245|380|568|705|781|909|947|954|781|LEB|leb|LB1|LB2|lb2|LBE|lbe|b6a|B6A)-[0-9]{2}[C-](?:\d{5}|\d{6}))$/i;
    return patt.test(id_number);
}
function check_national_id(id_number)
{
    return /^[0-9]{11}$/i.test(id_number);
}
