
function checkArabicOnly(field)
{
    checkFieldCharacters
    (
        field,
        function(ch)
        {
            var c = ch.charCodeAt(0);
            return !((c < 1536 || c > 1791) && ch != " ");
        }
    );
}
function checkEnglishOnly(field) {
    checkFieldCharacters(
        field,
        function(ch) {
            var c = ch.charCodeAt(0);
            return ((c >= 65 && c <= 90) ||    // A–Z
                    (c >= 97 && c <= 122) ||   // a–z
                    ch === " ");
        }
    );
}
function checkIsNumber(field)
{
    checkFieldCharacters
    (
        field,
        function(ch)
        {
            return checkCharacterIsNumber(ch);
        }
    );
}

function checkFieldCharacters(field,characterCheck)
{
    var sNewVal = "";

    var sFieldVal = field.val();

    for(var i = 0; i < sFieldVal.length; i++) {

        var ch = sFieldVal.charAt(i);

        if(!characterCheck(ch)) {
            // Discard
        }

        else {
            sNewVal += ch;
        }
    }

    if(field.val() != sNewVal) {
        field.val(sNewVal);
    }
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
