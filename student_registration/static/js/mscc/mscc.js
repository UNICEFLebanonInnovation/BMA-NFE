
var arabic_fields = "#id_child_first_name, #id_child_father_name, #id_child_last_name, #id_child_mother_fullname, " +
    " #id_caregiver_mother_name, #id_caregiver_last_name, #id_caregiver_middle_name, #id_caregiver_first_name";

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


    $('.show-progarmme-details').click(function(e){
        e.preventDefault();

        $('#programme-body-content').empty("");
        $('#programme-body-content').append("Loading...");
        $('#programmeModal').modal('show');

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            async: true,
            dataType: 'html',
            success: function (response) {
                $('#programme-body-content').empty("");
                $('#programme-body-content').append(response);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

    $('.show-view-all').click(function(e){
        e.preventDefault();

        $('#programme-body-content').empty("");
        $('#programme-body-content').append("Loading...");
        $('#programmeModal').modal('show');

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            async: true,
            dataType: 'html',
            success: function (response) {
                $('#programme-body-content').empty("");
                $('#programme-body-content').append(response);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

    $('.attendance_month').click(function(e){
        e.preventDefault();

        $('.app-drawer-overlay').removeClass('d-none');

        $.ajax({
            type: "GET",
            url: $(this).attr('data-href'),
            cache: false,
            async: true,
            dataType: 'html',
            success: function (response) {
                $('#tab-faq-1').empty("");
                $('#tab-faq-1').append(response);
                $('.app-drawer-overlay').addClass('d-none');
            },
            error: function(response) {
                console.log(response);
                $('.app-drawer-overlay').addClass('d-none');
            }
        });
    });

    $(document).on('click', '.show-child-details', function(e){
        e.preventDefault();

        $('#child-content').empty("");
        $('#child-content').append("Loading...");
        $('#childModal').modal('show');

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            async: true,
            dataType: 'html',
            success: function (response) {
                $('#child-content').empty("");
                $('#child-content').append(response);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

    $(document).on('change', 'select#id_source_of_identification', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_child_gender', function(){
        reorganizeForm();
    });

    $(document).on('change', '#id_id_type', function(){
        reorganizeForm();

        $('#id_case_number').val('');
        $('#id_case_number_confirm').val('');
        $('#id_individual_case_number').val('');
        $('#id_individual_case_number_confirm').val('');
        $('#id_parent_individual_case_number').val('');
        $('#id_parent_individual_case_number_confirm').val('');
        $('#id_recorded_number').val('');
        $('#id_recorded_number_confirm').val('');
        $('#id_national_number').val('');
        $('#id_national_number_confirm').val('');
        $('#id_syrian_national_number').val('');
        $('#id_syrian_national_number_confirm').val('');
        $('#id_sop_national_number').val('');
        $('#id_sop_national_number_confirm').val('');
        $('#id_parent_national_number').val('');
        $('#id_parent_national_number_confirm').val('');
        $('#id_parent_syrian_national_number').val('');
        $('#id_parent_syrian_national_number_confirm').val('');
        $('#id_parent_sop_national_number').val('');
        $('#id_parent_sop_national_number_confirm').val('');
        $('#id_parent_other_number').val('');
        $('#id_parent_other_number_confirm').val('');
        $('#id_other_number').val('');
        $('#id_other_number_confirm').val('');
//        Caregiver has no ID = 7
        if($(this).val() != 7){
            return true;
        }

    });
    reorganizeForm();

    $(document).on('change', 'select#id_child_have_children, select#id_child_nationality, select#id_main_caregiver, select#id_main_caregiver_nationality, select#id_have_labour, select#id_labour_type, select#id_child_have_sibling', function(){
         reorganizeForm();
    });
    $(document).on('change', 'select#id_student_nationality, select#id_have_labour_single_selection, select#id_labour_weekly_income', function(){
        reorganizeForm();
    });

    $(document).on('change',
      '#id_child_first_name, #id_child_father_name, #id_child_last_name, ' +
      '#id_child_mother_fullname, #id_child_gender, #id_child_birthday_year, ' +
      '#id_child_birthday_month, #id_child_birthday_day, #id_child_nationality',
      function () {
        var first_name = $('#id_child_first_name').val();
        var father_name = $('#id_child_father_name').val();
        var last_name = $('#id_child_last_name').val();
        var mother_fullname = $('#id_child_mother_fullname').val();
        var sex = $('#id_child_gender').val();
        var year = $('#id_child_birthday_year').val();
        var month = $('#id_child_birthday_month').val();
        var day = $('#id_child_birthday_day').val();
        var nationality = $('#id_child_nationality').val();

        if (first_name && father_name && last_name && year && month && day) {

          $('#search_loader').removeClass('hidden');
          $('#nfe_search_loader').removeClass('hidden');

          outreach_child_search();
          old_child_search();
          if ( mother_fullname && sex && nationality) {
            child_duplication_check();
        }
        }
      }
    );

    $(document).on('change', 'select#id_main_caregiver', function(){
        var main_caregiver = $('select#id_main_caregiver').val();
        if(main_caregiver == 'Father'){
            var father_name = $('#id_child_father_name').val();
            var last_name = $('#id_child_last_name').val();
            $('#id_caregiver_first_name').val(father_name);
            $('#id_caregiver_last_name').val(last_name);
        }
        else {
            $('#id_caregiver_first_name').val('');
            $('#id_caregiver_last_name').val('');
        }
    });

    $(document).on('blur', arabic_fields, function(){
        checkArabicOnly($(this));
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


//old student
function old_child_search() {

    if (isAddPage()) {

        var birthday_year = $('#id_child_birthday_year').val();
        var birthday_month = $('#id_child_birthday_month').val();
        var birthday_day = $('#id_child_birthday_day').val();
        var first_name = $('#id_child_first_name').val();
        var father_name = $('#id_child_father_name').val();
        var last_name = $('#id_child_last_name').val();

        var data = {
            birthday_year: birthday_year,
            birthday_month: birthday_month,
            birthday_day: birthday_day,
            first_name: first_name,
            father_name: father_name,
            last_name: last_name,
        };

        $.ajax({
            url: '/mscc/old-child-search/',
            dataType: "json",
            data: data,
            cache: false,
            async: true,
            success: function (response) {
                append_old_result(response);
            },
            error: function (response) {
                console.log(response);
                $('#nfe_search_loader').addClass('hidden');
            }
        });
    }
}

function child_duplication_check() {

    $('#child-duplication-error').hide();
    $('#submit-id-save').prop('disabled', false);

    var birthday_year = $('#id_child_birthday_year').val();
    var birthday_month = $('#id_child_birthday_month').val();
    var birthday_day = $('#id_child_birthday_day').val();
    var first_name = $('#id_child_first_name').val();
    var father_name = $('#id_child_father_name').val();
    var last_name = $('#id_child_last_name').val();
    var mother_fullname = $('#id_child_mother_fullname').val();
    var sex = $('#id_child_gender').val();
    var nationality = $('#id_child_nationality').val();

    if (birthday_year && birthday_month && birthday_day && first_name && father_name && last_name && mother_fullname && sex && nationality) {
        var data = {
            birthday_year: birthday_year,
            birthday_month: birthday_month,
            birthday_day: birthday_day,
            first_name: first_name,
            father_name: father_name,
            last_name: last_name,
            mother_fullname: mother_fullname,
            sex: sex,
            nationality: nationality
        };

        var path = window.location.pathname;
        var match = path.match(/Child-Edit\/([^\/]+)\//);
        if (match) {
            data.registration_id = match[1];
        }

        var requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        $.ajax({
            type: "POST",
            url: '/mscc/child-duplication-check/',
            data: JSON.stringify(data),
            cache: false,
            async: true,
            headers: requestHeaders,
            dataType: 'json',
            success: function (response) {
                if(response.result.length > 0){
                    var text = ''
                    $(response.result).each(function(i, item){
                        text = 'This <a class="show-child-details" data-toggle="modal" data-target=".bd-example-modal-lg-2" href="/mscc/child-profile-preview/?registry_id='+item.id+'">Child</a> is already registered under the MSCC progarmme in the Center: ' + item.center__name+'</br>';
                        text = text + 'Click <a href="/mscc/new-round/'+item.id+'/">here</a> to register this child in a new Round.'
                    })
                    $('#child-duplication-error-text').html(text);
                    $('#child-duplication-error').show();
                    $('#submit-id-save').prop('disabled', true);
                }
            },
            error: function (response) {
                console.log(response);
            }
        });
    }
}
function append_old_result(data)
{
    var child_html = '';
    $('#nfe_search_result').empty();
    $('#nfe_search_loader').addClass('hidden');

    if(data.result.error) {
        var html_line1 = '<div class="vertical-timeline-item vertical-timeline-element"><div><div class="vertical-timeline-element-icon bounce-in"><div class="timeline-icon border-warning"><i class="lnr-cross text-warning"></i></div></div><div class="vertical-timeline-element-content bounce-in">';
        var html_line2 = '<h4 class="timeline-title text-warning">'+ data.result.error +'</h4>';
        var html_line3 = '<p></p>';
        var html_line4 = '<p></p></div></div></div>';

        child_html = html_line1 + html_line2 + html_line3 + html_line4;

        $('#nfe_search_result').append(child_html);

        return true;
    }

    if(data.result.length == 0) {
        var html_line1 = '<div class="vertical-timeline-item vertical-timeline-element"><div><div class="vertical-timeline-element-icon bounce-in"><div class="timeline-icon border-danger"><i class="lnr-warning text-danger"></i></div></div><div class="vertical-timeline-element-content bounce-in">';
        var html_line2 = '<h4 class="timeline-title text-danger">No result found</h4>';
        var html_line3 = '<p></p>';
        var html_line4 = '<p></p></div></div></div>';

        child_html = html_line1 + html_line2 + html_line3 + html_line4;

        $('#nfe_search_result').append(child_html);

        return true;
    }

    $(data.result).each(function(i, item) {
        var full_name = "";
        full_name = full_name.concat(item.first_name, " ", item.father_name, " ", item.last_name);

        var html_line1 = '<div class="vertical-timeline-item vertical-timeline-element"><div><div class="vertical-timeline-element-icon bounce-in"><div class="timeline-icon border-success"><span class="text-success">'+ item.score +'%</span></div></div><div class="vertical-timeline-element-content bounce-in">';
        var html_line2 = '<h4 class="timeline-title text-success"><a href="javascript:get_old_child_data('+ item.id +');">'+full_name+'</a></h4>';
        var html_line3 = '<p>'+ item.birthday_day + '/'+ item.birthday_month + '/'+ item.birthday_year + ' - '+ item.mother_fullname +'</p>';
        var html_line4 = '<p>'+ item.sex + ' - '+ item.nationality__name +'</p>';
        var html_line5 = '<p>'+ item.programmes +'</p></div></div></div>';
        child_html = html_line1 + html_line2 + html_line3 + html_line4 + html_line5;

        $('#nfe_search_result').append(child_html);

        return true;
    });

}

function get_old_child_data(student_id)
{
    $('#nfe_search_loader').removeClass('hidden');

    $.ajax({
        url: '/mscc/get-old-child-data/',
        data: { student_id: student_id},
        cache: false,
        async: true,
        dataType: 'json',
        success: function (response) {
            fill_old_child_data(response);
        },
        error: function (response) {
            console.log(response);
        }
    });
}

function fill_old_child_data(data)
{
    $('#nfe_search_loader').addClass('hidden');
    $(data).each(function(i, item) {
        console.log(item);
        {
            Object.keys(item).forEach(key => {
                $('#id_'+ key).val(item[key]);
            });
        }
    });
    $('#nfe_search_loader').addClass('hidden');
}

function reorganizeForm()
{
//  child_gender
    var child_gender = $('select#id_child_gender').val();
    var package_type = $('#id_type').val();

    if (package_type == 'Core-Package') {
        $('#id_first_phone_number').prop('required', true);
        $('#id_first_phone_number_confirm').prop('required', true);
    } else {
        $('#id_first_phone_number').prop('required', false);
        $('#id_first_phone_number_confirm').prop('required', false);
    }

    if(child_gender =='Female'){
        $("#id_child_have_children").append('<option value="Child pregnant or expecting children">Child pregnant or expecting children</option>');
    }
    else
     {
        $("#id_child_have_children option[value='Child pregnant or expecting children']").remove();
    }

//    Child Nationality
    var child_nationality = $('select#id_child_nationality').val();
    $('div#div_id_child_nationality_other').addClass('d-none');
//    $('#child_nationality_other_badge').addClass('d-none');

    if(child_nationality == 6){
        $('#div_id_child_nationality_other').removeClass('d-none');
//        $('#child_nationality_other_badge').removeClass('d-none');
    }
    else{
        $('#id_child_nationality_other').val('');
    }

    if(child_nationality == 5 && $('#id_type').val() == 'Walk-in'){
        $('#child_fe_unique_id_block').removeClass('d-none');
    }
    else{
        $('#child_fe_unique_id_block').addClass('d-none');
        $('#id_child_fe_unique_id').val('');
    }

//    Child have children
    var child_have_children = $('select#id_child_have_children').val();

    if(child_have_children =='Yes'){
        $('div#div_id_child_children_number').removeClass('d-none');
//        $('#child_children_number_badge').removeClass('d-none');
    }
    else{
        $('div#div_id_child_children_number').addClass('d-none');
//        $('#child_children_number_badge').addClass('d-none');
        $('#id_child_children_number').val('');
    }

    //child_have_sibling
    var child_have_sibling = $('select#id_child_have_sibling').val();

    if(child_have_sibling =='Yes'){
        $('div#div_id_child_siblings_have_disability').removeClass('d-none');
//        $('#child_siblings_have_disability_badge').removeClass('d-none');
    }
    else{
        $('div#div_id_child_siblings_have_disability').addClass('d-none');
//        $('#child_siblings_have_disability_badge').addClass('d-none');
        $('#id_child_siblings_have_disability').val('');
    }

//   Source of Identification
    var source_of_identification = $('select#id_source_of_identification').val();
    $('div#div_id_source_of_identification_specify').addClass('d-none');
//    $('#source_of_identification_specify_badge').addClass('d-none');

    if(source_of_identification == 'Other Sources'){
        $('#div_id_source_of_identification_specify').removeClass('d-none');
//        $('#source_of_identification_specify_badge').removeClass('d-none');
    }

//    Main Caregiver
    var main_caregiver = $('select#id_main_caregiver').val();
    $('div#div_id_main_caregiver_other').addClass('d-none');
    if(main_caregiver == 'Other'){
        $('#div_id_main_caregiver_other').removeClass('d-none');
    }
    else
    {
        $('#id_main_caregiver_other').val('');
    }

//    Main Caregiver Nationality
    var main_caregiver_nationality = $('select#id_main_caregiver_nationality').val();
    $('div#div_id_main_caregiver_nationality_other').addClass('d-none');
    if(main_caregiver_nationality == 6){
        $('#div_id_main_caregiver_nationality_other').removeClass('d-none');
    }
    else
    {
        $('#id_main_caregiver_nationality_other').val('');
    }


//    ID Type
    var id_type = $('select#id_id_type').val();

/*  1	"UNHCR Registered"
    2	"UNHCR Recorded"
    3	"Syrian national ID"
    4	"Palestinian national ID"
    5	"Lebanese national ID"
    6	"Other nationality"
    7	"Caregiver has no ID" */

    $('div.child_id').addClass('d-none');
    if(id_type == 1){
        $('div.child_id1').removeClass('d-none');
    }

    if(id_type == 2){
        $('div.child_id2').removeClass('d-none');
    }

    if(id_type == 5){
        $('div.child_id3').removeClass('d-none');
    }

    if(id_type == 3){
        $('div.child_id4').removeClass('d-none');
    }

    if(id_type == 4){
        $('div.child_id5').removeClass('d-none');
    }

    if(id_type == 6){
        $('div.child_id6').removeClass('d-none');
    }

    if(id_type == 9){
        $('div.child_id7').removeClass('d-none');
    }

    //  Labour
    var have_labour = $('select#id_have_labour').val();
    if(have_labour == '' || have_labour == 'No'){
        $('div#div_id_labour_type').addClass('d-none');
        $('#labour_details_1').addClass('d-none');
        $('#labour_details_2').addClass('d-none');
        $('#labour_details_3').addClass('d-none');
        $('#id_labour_type').val('')
        $('#id_labour_type_specify').val('')
        $('#id_labour_hours').val('')
        $('#id_labour_weekly_income').val('')
        $('#labour_condition').val('')
    }
    else
    {
        $('div#div_id_labour_type').removeClass('d-none');
        $('#labour_details_1').removeClass('d-none');
        $('#labour_details_2').removeClass('d-none');
        $('#labour_details_3').removeClass('d-none');
    }

    var labour_type = $('select#id_labour_type').val();
    if(labour_type == 'Other services'){
        $('div#div_id_labour_type_specify').removeClass('d-none');
    }
    else
    {
        $('div#div_id_labour_type_specify').addClass('d-none');
        $('#id_labour_type_specify').val('');
    }
}


// main_form_validation.js merged into mscc.js
// Client-side validation for MSCC MainForm with realtime feedback
var phoneRegex = /^((03|70|71|76|78|79|81|86)-\d{6})$/;
var regexMap = {
    '#id_first_phone_number': phoneRegex,
    '#id_first_phone_number_confirm': phoneRegex,
    '#id_second_phone_number': phoneRegex,
    '#id_second_phone_number_confirm': phoneRegex,
    '#id_case_number': /^((245|380|568|705|781|909|947|954|781|LEB|leb|LB1|LB2|lb2|LBE|lbe|b6a|B6A)-[0-9]{2}[C-](?:\d{5}|\d{6}))$/,
    '#id_case_number_confirm': /^((245|380|568|705|781|909|947|954|781|LEB|leb|LB1|LB2|lb2|LBE|lbe|b6a|B6A)-[0-9]{2}[C-](?:\d{5}|\d{6}))$/,
    '#id_parent_individual_case_number': /^((245|380|568|705|781|909|947|954|781|LEB|leb|LB1|LB2|lb2|LBE|lbe|b6a|B6A)-[0-9]{8})$/,
    '#id_parent_individual_case_number_confirm': /^((245|380|568|705|781|909|947|954|781|LEB|leb|LB1|LB2|lb2|LBE|lbe|b6a|B6A)-[0-9]{8})$/,
    '#id_individual_case_number': /^((245|380|568|705|781|909|947|954|781|LEB|leb|LB1|LB2|lb2|LBE|lbe|b6a|B6A)-[0-9]{8})$/,
    '#id_individual_case_number_confirm': /^((245|380|568|705|781|909|947|954|781|LEB|leb|LB1|LB2|lb2|LBE|lbe|b6a|B6A)-[0-9]{8})$/,
    '#id_recorded_number': /^((245|380|568|705|781|909|947|954|781|LEB|leb|LB1|LB2|lb2|LBE|lbe|b6a|B6A)-[0-9]{2}[C-](?:\d{5}|\d{6})|LB-\d{3}-\d{6}|\d{7}|86A-\d{2}-\d{5})$/,
    '#id_recorded_number_confirm': /^((245|380|568|705|781|909|947|954|781|LEB|leb|LB1|LB2|lb2|LBE|lbe|b6a|B6A)-[0-9]{2}[C-](?:\d{5}|\d{6})|LB-\d{3}-\d{6}|\d{7}|86A-\d{2}-\d{5})$/,
    '#id_national_number': /^\d{12}$/,
    '#id_national_number_confirm': /^\d{12}$/,
    '#id_syrian_national_number': /^\d{11}$/,
    '#id_syrian_national_number_confirm': /^\d{11}$/,
    '#id_parent_national_number': /^\d{12}$/,
    '#id_parent_national_number_confirm': /^\d{12}$/,
    '#id_parent_syrian_national_number': /^\d{11}$/,
    '#id_parent_syrian_national_number_confirm': /^\d{11}$/
};

function clearErrors() {
    $('.error-field').removeClass('error-field');
    $('.field-error').remove();
}

function showError(selector, message) {
    var field = $(selector);
    if (field.attr('type') === 'checkbox') {
        var name = field.attr('name');
        var checkboxes = $('input[name="' + name + '"]');
        if (checkboxes.length > 1) {
            checkboxes.addClass('error-field');
            var group = field.closest('.form-group');
            var label = group.find('label').first();
            var errorEl = label.next('.field-error');
            if (!errorEl.length) {
                errorEl = $('<div class="help-block field-error"></div>');
                errorEl.insertAfter(label);
            }
            errorEl.text(message);
            return;
        }
    }
    field.addClass('error-field');
    var errorEl = field.next('.field-error');
    if (!errorEl.length) {
        errorEl = $('<div class="help-block field-error"></div>');
        errorEl.insertAfter(field);
    }
    errorEl.text(message);
}

function validateField(field) {
    var selector = '#' + field.attr('id');
    field.removeClass('error-field');
    field.next('.field-error').remove();

    if (field.prop('required') && field.is(':visible') && !field.val()) {
        showError(selector, 'This field is required');
        return;
    }

    if (regexMap[selector]) {
        var val = field.val();
        if (val && !regexMap[selector].test(val)) {
            var placeholder = field.attr('placeholder');
            var msg = 'Please enter a valid value';
            if (selector.indexOf('phone') !== -1) {
                msg = 'Please enter a valid phone number (XX-XXXXXX)';
            } else if (placeholder) {
                msg = 'Please follow the format ' + placeholder.replace('Format:', '').trim();
            }
            showError(selector, msg);
        }
    }
}

function validateMainForm(showModal, step) {
    if (showModal === undefined) showModal = true;
    var valid = true;

    var requiredFields = [
        '#id_child_first_name',
        '#id_child_father_name',
        '#id_child_last_name',
        '#id_child_mother_fullname',
        '#id_child_gender',
        '#id_child_nationality',
        '#id_child_disability',
        '#id_child_marital_status',
        '#id_child_have_children',
        '#id_child_have_sibling',
        '#id_child_mother_pregnant_expecting',
        '#id_source_of_identification'
    ];

    var minValueMap = {
        '#id_child_children_number': 0,
        '#id_children_number_under18': 0,
        '#id_labour_hours': 0
    };

    var maxLengthMap = {
        '#id_child_children_number': 4,
        '#id_children_number_under18': 4,
        '#id_labour_hours': 4
    };
    clearErrors();

    requiredFields.forEach(function(selector) {
        var field = $(selector);
        if (!field.is(':visible')) return;
        if (!field.val()) {
            showError(selector, 'This field is required');
            valid = false;
        }
    });

    // Date validation
    var year = parseInt($('#id_child_birthday_year').val()) || 0;
    var month = parseInt($('#id_child_birthday_month').val()) || 0;
    var day = parseInt($('#id_child_birthday_day').val()) || 0;
    if (year && month && day) {
        var dt = new Date(year, month - 1, day);
        if (dt.getFullYear() !== year || dt.getMonth() !== month - 1 || dt.getDate() !== day) {
            showError('#id_child_birthday_year', 'The date is not valid.');
            valid = false;
        }
    } else {
        if (!year) showError('#id_child_birthday_year', 'This field is required');
        if (!month) showError('#id_child_birthday_month', 'This field is required');
        if (!day) showError('#id_child_birthday_day', 'This field is required');
        valid = false;
    }

    // Child nationality other
    if ($('#id_child_nationality').val() == '6' && $('#id_child_nationality_other').val() === '') {
        showError('#id_child_nationality_other', 'This field is required');
        valid = false;
    }

    // Child have children
    if ($('#id_child_have_children').val() == 'Yes' && $('#id_child_children_number').val() === '') {
        showError('#id_child_children_number', 'This field is required');
        valid = false;
    }

    // Child have sibling
    if ($('#id_child_have_sibling').val() == 'Yes' && $('#id_child_siblings_have_disability').val() === '') {
        showError('#id_child_siblings_have_disability', 'This field is required');
        valid = false;
    }

    // Source of identification
    if ($('#id_source_of_identification').val() == 'Other Sources' && $('#id_source_of_identification_specify').val() === '') {
        showError('#id_source_of_identification_specify', 'This field is required');
        valid = false;
    }

    if (step === 1) {
        return valid;
    }

    var package_type = $('#id_type').val();
    if (package_type == 'Core-Package') {
        if ($('#id_father_educational_level').val() === '') {
            showError('#id_father_educational_level', 'This field is required');
            valid = false;
        }
        if ($('#id_mother_educational_level').val() === '') {
            showError('#id_mother_educational_level', 'This field is required');
            valid = false;
        }
        var first_phone = $('#id_first_phone_number').val();
        var first_phone_confirm = $('#id_first_phone_number_confirm').val();
        if ($('#id_first_phone_owner').val() === '') {
            showError('#id_first_phone_owner', 'This field is required');
            valid = false;
        }
        if (first_phone === '') {
            showError('#id_first_phone_number', 'This field is required');
            valid = false;
        }
        if (first_phone_confirm === '') {
            showError('#id_first_phone_number_confirm', 'This field is required');
            valid = false;
        }
        if (first_phone !== first_phone_confirm) {
            showError('#id_first_phone_number_confirm', 'The phone numbers are not matched');
            valid = false;
        }
        var second_phone = $('#id_second_phone_number').val();
        var second_phone_confirm = $('#id_second_phone_number_confirm').val();
        if (second_phone !== second_phone_confirm) {
            showError('#id_second_phone_number_confirm', 'The phone numbers are not matched');
            valid = false;
        }
        var main_caregiver = $('#id_main_caregiver').val();
        if (main_caregiver === '') {
            showError('#id_main_caregiver', 'This field is required');
            valid = false;
        }
        if (main_caregiver == 'Other' && $('#id_main_caregiver_other').val() === '') {
            showError('#id_main_caregiver_other', 'This field is required');
            valid = false;
        }
        if ($('#id_main_caregiver_nationality').val() == '6' && $('#id_main_caregiver_nationality_other').val() === '') {
            showError('#id_main_caregiver_nationality_other', 'This field is required');
            valid = false;
        }
        if ($('#id_children_number_under18').val() === '') {
            showError('#id_children_number_under18', 'This field is required');
            valid = false;
        }
        if ($('#id_caregiver_first_name').val() === '') {
            showError('#id_caregiver_first_name', 'This field is required');
            valid = false;
        }
        if ($('#id_caregiver_middle_name').val() === '') {
            showError('#id_caregiver_middle_name', 'This field is required');
            valid = false;
        }
        if ($('#id_caregiver_last_name').val() === '') {
            showError('#id_caregiver_last_name', 'This field is required');
            valid = false;
        }
        if ($('#id_caregiver_mother_name').val() === '') {
            showError('#id_caregiver_mother_name', 'This field is required');
            valid = false;
        }
        var have_labour = $('#id_have_labour').val();
        if (have_labour === '') {
            showError('#id_have_labour', 'This field is required');
            valid = false;
        }
        if (have_labour != 'No') {
            if ($('#id_labour_type').val() === '') {
                showError('#id_labour_type', 'This field is required');
                valid = false;
            } else if ($('#id_labour_type').val() == 'Other services' && $('#id_labour_type_specify').val() === '') {
                showError('#id_labour_type_specify', 'This field is required');
                valid = false;
            }
            if ($('#id_labour_hours').val() === '') {
                showError('#id_labour_hours', 'This field is required');
                valid = false;
            }
            if ($('#id_labour_weekly_income').val() === '') {
                showError('#id_labour_weekly_income', 'This field is required');
                valid = false;
            }
            if ($('input[name="labour_condition"]:checked').length === 0) {
                showError('input[name="labour_condition"]:first', 'This field is required');
                valid = false;
            }
        }
        var id_type = $('#id_id_type').val();
        var case_number = $('#id_case_number').val();
        var case_confirm = $('#id_case_number_confirm').val();
        var parent_case = $('#id_parent_individual_case_number').val();
        var parent_case_confirm = $('#id_parent_individual_case_number_confirm').val();
        var individual_case = $('#id_individual_case_number').val();
        var individual_case_confirm = $('#id_individual_case_number_confirm').val();
        var recorded = $('#id_recorded_number').val();
        var recorded_confirm = $('#id_recorded_number_confirm').val();
        var parent_syrian = $('#id_parent_syrian_national_number').val();
        var parent_syrian_confirm = $('#id_parent_syrian_national_number_confirm').val();
        var syrian = $('#id_syrian_national_number').val();
        var syrian_confirm = $('#id_syrian_national_number_confirm').val();
        var parent_sop = $('#id_parent_sop_national_number').val();
        var parent_sop_confirm = $('#id_parent_sop_national_number_confirm').val();
        var sop = $('#id_sop_national_number').val();
        var sop_confirm = $('#id_sop_national_number_confirm').val();
        var parent_nat = $('#id_parent_national_number').val();
        var parent_nat_confirm = $('#id_parent_national_number_confirm').val();
        var nat = $('#id_national_number').val();
        var nat_confirm = $('#id_national_number_confirm').val();
        var parent_other = $('#id_parent_other_number').val();
        var parent_other_confirm = $('#id_parent_other_number_confirm').val();
        var other = $('#id_other_number').val();
        var other_confirm = $('#id_other_number_confirm').val();
        var parent_extract = $('#id_parent_extract_record').val();
        var parent_extract_confirm = $('#id_parent_extract_record_confirm').val();

        Object.keys(regexMap).forEach(function(selector) {
            var field = $(selector);
            if (!field.is(':visible')) return;
            var val = field.val();
            if (val && !regexMap[selector].test(val)) {
                var placeholder = $(selector).attr('placeholder');
                var msg = 'Please enter a valid value';
                if (selector.indexOf('phone') !== -1) {
                    msg = 'Please enter a valid phone number (XX-XXXXXX)';
                } else if (placeholder) {
                    msg = 'Please follow the format ' + placeholder.replace('Format:', '').trim();
                }
                showError(selector, msg);
                valid = false;
            }
        });

        Object.keys(minValueMap).forEach(function(selector) {
            var field = $(selector);
            if (!field.is(':visible')) return;
            var val = field.val();
            var min = minValueMap[selector];
            if (val && parseInt(val, 10) < min) {
                showError(selector, 'Value must be at least ' + min);
                valid = false;
            }
        });

        Object.keys(maxLengthMap).forEach(function(selector) {
            var field = $(selector);
            if (!field.is(':visible')) return;
            var val = field.val();
            var maxLen = maxLengthMap[selector];
            if (val && val.length > maxLen) {
                showError(selector, 'Ensure this value has at most ' + maxLen + ' characters.');
                valid = false;
            }
        });

        if (id_type == '1') {
            if (case_number === '') {
                showError('#id_case_number', 'This field is required');
                valid = false;
            }
            if (case_number !== case_confirm) {
                showError('#id_case_number_confirm', 'The case numbers are not matched');
                valid = false;
            }
            if (parent_case !== parent_case_confirm) {
                showError('#id_parent_individual_case_number_confirm', 'The individual case numbers are not matched');
                valid = false;
            }
            if (individual_case !== individual_case_confirm) {
                showError('#id_individual_case_number_confirm', 'The individual case numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '2') {
            if (recorded === '') {
                showError('#id_recorded_number', 'This field is required');
                valid = false;
            }
            if (recorded !== recorded_confirm) {
                showError('#id_recorded_number_confirm', 'The recorded numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '3') {
            if (parent_syrian === '') {
                showError('#id_parent_syrian_national_number', 'This field is required');
                valid = false;
            }
            if (parent_syrian_confirm === '') {
                showError('#id_parent_syrian_national_number_confirm', 'This field is required');
                valid = false;
            }
            if (parent_syrian !== parent_syrian_confirm) {
                showError('#id_parent_syrian_national_number_confirm', 'The national numbers are not matched');
                valid = false;
            }
            if (syrian !== syrian_confirm) {
                showError('#id_syrian_national_number_confirm', 'The national numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '4') {
            if (parent_sop === '') {
                showError('#id_parent_sop_national_number', 'This field is required');
                valid = false;
            }
            if (parent_sop_confirm === '') {
                showError('#id_parent_sop_national_number_confirm', 'This field is required');
                valid = false;
            }
            if (parent_sop !== parent_sop_confirm) {
                showError('#id_parent_sop_national_number_confirm', 'The national numbers are not matched');
                valid = false;
            }
            if (sop !== sop_confirm) {
                showError('#id_sop_national_number_confirm', 'The national numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '5') {
            if (parent_nat !== parent_nat_confirm) {
                showError('#id_parent_national_number_confirm', 'The national numbers are not matched');
                valid = false;
            }
            if (nat !== nat_confirm) {
                showError('#id_national_number_confirm', 'The national numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '6') {
            if (parent_other === '') {
                showError('#id_parent_other_number', 'This field is required');
                valid = false;
            }
            if (parent_other_confirm === '') {
                showError('#id_parent_other_number_confirm', 'This field is required');
                valid = false;
            }
            if (parent_other !== parent_other_confirm) {
                showError('#id_parent_other_number_confirm', 'The ID numbers are not matched');
                valid = false;
            }
            if (other !== other_confirm) {
                showError('#id_other_number_confirm', 'The ID numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '9') {
            if (parent_extract !== parent_extract_confirm) {
                showError('#id_parent_extract_record_confirm', 'The Parent Extract Record are not matched');
                valid = false;
            }
        }

        if ($('#id_caregiver_mother_name').val() === '') {
            showError('#id_caregiver_mother_name', 'This field is required');
            valid = false;
        }
        if ($('#id_child_living_arrangement').val() === '') {
            showError('#id_child_living_arrangement', 'This field is required');
            valid = false;
        }
//        if ($('#id_cash_support_programmes').val() === '') {
//            showError('#id_cash_support_programmes', 'This field is required');
//            valid = false;
//        }
    }

    if (showModal && !valid) {
        var missingByStep = {};
        $('.error-field').each(function() {
            var field = $(this);
            var stepDiv = field.closest('div[id^="step-"]');
            var stepId = stepDiv.length ? stepDiv.attr('id') : 'step-1';
            var stepNum = stepId.split('-')[1];
            if (!missingByStep[stepNum]) {
                missingByStep[stepNum] = [];
            }
            var label = $('label[for="' + field.attr('id') + '"]').clone().children().remove().end().text().trim();
            if (!label) {
                label = field.attr('name') || field.attr('id');
            }
            if (missingByStep[stepNum].indexOf(label) === -1) {
                missingByStep[stepNum].push(label);
            }
        });
        var content = '';
        Object.keys(missingByStep).sort().forEach(function(stepKey) {
            content += '<strong>Step ' + stepKey + ':</strong><ul>';
            missingByStep[stepKey].forEach(function(label) {
                content += '<li>' + label + '</li>';
            });
            content += '</ul>';
        });
        $('#formErrorModal #swal2-content').html(content);
        $('#formErrorModal').modal('show');
    }

    return valid;
}

$(document).ready(function() {
    $('form').on('submit', function(e) {
        var step = $('#step-1').is(':visible') ? 1 : null;
        if (!validateMainForm(true, step)) {
            e.preventDefault();
        }
    });

    $('input, select').on('change input blur', function() {
        validateField($(this));
        var step = $('#step-1').is(':visible') ? 1 : null;
        validateMainForm(false, step);
    });

    $('#formErrorModal').on('hidden.bs.modal', function(){
        $('#formErrorModal #swal2-content').text('Please check the form mandatory fields.');
    });
});
