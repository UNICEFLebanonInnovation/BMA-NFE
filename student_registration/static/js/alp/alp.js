function translateMessage(message) {
    return window.gettext ? window.gettext(message) : message;
}



var arabic_fields = "#id_child_first_name, #id_child_father_name, #id_child_last_name, #id_child_mother_fullname, " +
    " #id_caregiver_mother_name, #id_caregiver_last_name, #id_caregiver_middle_name, #id_caregiver_first_name";

var isDuplicateFound = false;

$(document).ready(function() {

    $("#submit-id-save").click(function(e){
        var form = $(this).closest('form')[0];
        var valid = form.checkValidity();

        if (typeof validateMainForm === 'function') {
            valid = validateMainForm(true) && valid;
        }

        if (valid) {
            $(this).prop('disabled', true);
            $(form).triggerHandler('submit');
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

    $(document).on('change', 'select#id_child_have_children, select#id_child_nationality, select#id_child_disability, select#id_main_caregiver, select#id_main_caregiver_nationality, select#id_have_labour, select#id_labour_type, select#id_child_have_sibling', function(){
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
          $('#nfe_search_loader').removeClass('d-none');

          if (typeof outreach_child_search === 'function') outreach_child_search();

          if (mother_fullname && sex && nationality) {
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
        $(this).removeClass('is-invalid');
        var currentStepNum = $('.step-content:visible').attr('id').split('-')[1];
        if(typeof validateMainForm === 'function' && validateMainForm(true, parseInt(currentStepNum))){
            $('#next-btn').trigger('click');
        }
    });


});

function child_duplication_check() {

    isDuplicateFound = false;
    $('#child-duplication-error').hide();
    $('#submit-id-save').prop('disabled', false);
    $('#next-btn').prop('disabled', false);
    $('#nfe_search_result').closest('.card').find('.card-header').removeClass('bg-danger').addClass('bg-primary');

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
        var match = path.match(/registrations\/edit\/([^\/]+)\//i);
        if (match) {
            data.registration_id = match[1];
        }

        var requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        $.ajax({
            type: "POST",
            url: '/alp/child-duplication-check/',
            data: JSON.stringify(data),
            cache: false,
            async: true,
            headers: requestHeaders,
            dataType: 'json',
            success: function (response) {
                if(response.result.length > 0){
                    isDuplicateFound = true;
                    var text = ''
                    var $container = $('#nfe_search_result');
                    $container.empty();
                    $('#nfe_search_result').closest('.card').find('.card-header').removeClass('bg-primary').addClass('bg-danger');

                    $(response.result).each(function(i, item){
                        text = 'This child is already registered in the ALP programme at school: ' + (item.school__name || '-') + '.';

                        var full_name = item.child__first_name + " " + item.child__father_name + " " + item.child__last_name;
                        var html = `
                            <div class="list-group-item p-3 border-danger border-start border-4 bg-danger bg-opacity-10 mb-2">
                                <div class="d-flex w-100 justify-content-between align-items-center mb-2">
                                    <h6 class="mb-0 fw-bold text-danger">${full_name}</h6>
                                    <span class="badge bg-danger">DUPLICATE</span>
                                </div>
                                <p class="mb-1 small text-dark">
                                    <i class="bi bi-calendar-event me-1"></i> ${item.child__birthday_day}/${item.child__birthday_month}/${item.child__birthday_year}
                                    <br>
                                    <i class="bi bi-person-heart me-1"></i> ${item.child__mother_fullname}
                                </p>
                                <div class="small text-muted mb-3">
                                    <i class="bi bi-geo-alt me-1"></i> ${item.school__name || "-"}
                                </div>
                                <a href="/alp/child-profile/${item.id}/" class="btn btn-danger btn-sm w-100 fw-bold">
                                    <i class="bi bi-eye-fill me-1"></i> View existing registration
                                </a>
                            </div>`;
                        $container.prepend(html);
                    })
                    $('#child-duplication-error-text').html(text);
                    $('#child-duplication-error').show();
                    $('#submit-id-save').prop('disabled', true);
                    $('#next-btn').prop('disabled', true);
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
    if (isDuplicateFound) return;

    var $container = $('#nfe_search_result');
    $container.empty();
    $('#nfe_search_loader').addClass('d-none');

    if(data.result.error) {
        $container.append('<div class="list-group-item text-warning p-3"><i class="bi bi-exclamation-triangle me-2"></i>' + data.result.error + '</div>');
        return true;
    }

    if(data.result.length == 0) {
        $container.append('<div class="list-group-item text-muted p-4 text-center"><i class="bi bi-search fs-2 d-block mb-2 opacity-25"></i> No matches found</div>');
        return true;
    }

    $(data.result).each(function(i, item) {
        var full_name = item.first_name + " " + item.father_name + " " + item.last_name;
        var scoreClass = item.score > 85 ? 'text-danger fw-bold' : 'text-success';

        var html = `
            <a href="javascript:get_old_child_data(${item.id});" class="list-group-item list-group-item-action p-3">
                <div class="d-flex w-100 justify-content-between align-items-center">
                    <h6 class="mb-1 fw-bold text-primary">${full_name}</h6>
                    <span class="badge rounded-pill bg-light border text-dark ${scoreClass}">${item.score}%</span>
                </div>
                <p class="mb-1 small text-dark">
                    <i class="bi bi-calendar-event me-1"></i> ${item.birthday_day}/${item.birthday_month}/${item.birthday_year}
                    <span class="mx-1">|</span>
                    <i class="bi bi-person-heart me-1"></i> ${item.mother_fullname}
                </p>
                <div class="small text-muted">
                    <i class="bi bi-gender-ambiguous me-1"></i> ${item.sex}
                    <span class="mx-2">|</span>
                    <i class="bi bi-flag me-1"></i> ${item.nationality__name}
                </div>
                ${item.programmes ? `<div class="mt-2"><span class="badge bg-info-subtle text-info border-info border-opacity-25 fw-normal">${item.programmes}</span></div>` : ''}
            </a>`;

        $container.append(html);
    });
    return true;
}

function get_old_child_data(student_id)
{
    $('#nfe_search_loader').removeClass('hidden');

    $.ajax({
        url: '/alp/get-old-child-data/',
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

    $('#id_first_phone_number').prop('required', true);
    $('#id_first_phone_number_confirm').prop('required', true);

    if(child_gender =='Female'){
        $("#id_child_have_children").append('<option value="Child pregnant or expecting children">Child pregnant or expecting children</option>');
    }
    else
     {
        $("#id_child_have_children option[value='Child pregnant or expecting children']").remove();
    }

//    Child Nationality
    var child_nationality = $('select#id_child_nationality').val();
    //$('div#div_id_child_nationality_other').addClass('d-none').hide();

//    Child Disability Other
    var child_disability = $('select#id_child_disability option:selected').text();
    if(child_disability == 'Other' || child_disability == 'غير ذلك'){
        //$('#div_id_child_disability_other').removeClass('d-none').show();
    }
    else{
       // $('#div_id_child_disability_other').addClass('d-none').hide();
       // $('#id_child_disability_other').val('');
    }

    if(child_nationality == 6){
        $('#div_id_child_nationality_other').removeClass('d-none').show();
    }
    else{
        $('#id_child_nationality_other').val('');
    }

    if(child_nationality == 5 && $('#id_type').val() == 'Walk-in'){
        $('#child_fe_unique_id_block').removeClass('d-none').show();
    }
    else{
//        $('#child_fe_unique_id_block').addClass('d-none').hide();
        $('#id_child_fe_unique_id').val('');
    }

//    Child have children
    var child_have_children = $('select#id_child_have_children').val();

    if(child_have_children =='Yes'){
        //$('div#div_id_child_children_number').removeClass('d-none').show();
    }
    else{
//        $('div#div_id_child_children_number').addClass('d-none').hide();
        $('#id_child_children_number').val('');
    }

    //child_have_sibling
    var child_have_sibling = $('select#id_child_have_sibling').val();

    if(child_have_sibling =='Yes'){
        $('div#div_id_child_siblings_have_disability').removeClass('d-none').show();
    }
    else{
//        $('div#div_id_child_siblings_have_disability').addClass('d-none').hide();
        $('#id_child_siblings_have_disability').val('');
    }

//   Source of Identification
    var source_of_identification = $('select#id_source_of_identification').val();
//    $('div#div_id_source_of_identification_specify').addClass('d-none').hide();

    if(source_of_identification == 'Other Sources'){
        $('#div_id_source_of_identification_specify').removeClass('d-none').show();
    }

//    Main Caregiver
    var main_caregiver = $('select#id_main_caregiver').val();
//    $('div#div_id_main_caregiver_other').addClass('d-none').hide();
    if(main_caregiver == 'Other'){
        $('#div_id_main_caregiver_other').removeClass('d-none').show();
    }
    else
    {
        $('#id_main_caregiver_other').val('');
    }

//    Main Caregiver Nationality
    var main_caregiver_nationality = $('select#id_main_caregiver_nationality').val();
//    $('div#div_id_main_caregiver_nationality_other').addClass('d-none').hide();
    if(main_caregiver_nationality == 6){
        $('#div_id_main_caregiver_nationality_other').removeClass('d-none').show();
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

    $('div.child_id').addClass('d-none').hide();
    if(id_type == 1){
        $('div.child_id1').removeClass('d-none').show();
    }

    if(id_type == 2){
        $('div.child_id2').removeClass('d-none').show();
    }

    if(id_type == 5){
        $('div.child_id3').removeClass('d-none').show();
    }

    if(id_type == 3){
        $('div.child_id4').removeClass('d-none').show();
    }

    if(id_type == 4){
        $('div.child_id5').removeClass('d-none').show();
    }

    if(id_type == 6){
        $('div.child_id6').removeClass('d-none').show();
    }

    if(id_type == 9){
        $('div.child_id7').removeClass('d-none').show();
    }

    //  Labour
    var have_labour = $('select#id_have_labour').val();
    if(have_labour == '' || have_labour == 'No'){
//        $('div#div_id_labour_type').addClass('d-none').hide();
//        $('#labour_details_1').addClass('d-none').hide();
//        $('#labour_details_2').addClass('d-none').hide();
//        $('#labour_details_2_alt').addClass('d-none').hide();
//        $('#labour_details_3').addClass('d-none').hide();
        $('#id_labour_type').val('');
        $('#id_labour_type_specify').val('');
        $('#id_labour_hours').val('');
        $('#id_labour_weekly_income').val('');
        $('input[name="labour_condition"]').prop('checked', false);
    }
    else
    {
        $('div#div_id_labour_type').removeClass('d-none').show();
        $('#labour_details_1').removeClass('d-none').show();
        $('#labour_details_2').removeClass('d-none').show();
        $('#labour_details_2_alt').removeClass('d-none').show();
        $('#labour_details_3').removeClass('d-none').show();
    }

    var labour_type = $('select#id_labour_type').val();
    if(labour_type == 'Other services'){
        $('div#div_id_labour_type_specify').removeClass('d-none').show();
    }
    else
    {
//        $('div#div_id_labour_type_specify').addClass('d-none').hide();
        $('#id_labour_type_specify').val('');
    }
}


// main_form_validation.js merged into alp.js
// Client-side validation for MSCC MainForm with realtime feedback
var phoneRegex = /^((03|70|71|76|78|79|81|86)-\d{6})$/;
var regexMap = {
    '#id_first_phone_number': phoneRegex,
    '#id_first_phone_number_confirm': phoneRegex,
    '#id_second_phone_number': phoneRegex,
    '#id_second_phone_number_confirm': phoneRegex,
    '#id_case_number': /^((245|380|568|705|781|909|947|954|LEB|LB1|LB2|LBE|B6A)-[0-9]{2}[C-](?:\d{5}|\d{6}))$/i,
    '#id_case_number_confirm': /^((245|380|568|705|781|909|947|954|LEB|LB1|LB2|LBE|B6A)-[0-9]{2}[C-](?:\d{5}|\d{6}))$/i,
    '#id_parent_individual_case_number': /^((245|380|568|705|781|909|947|954|LEB|LB1|LB2|LBE|B6A)-[0-9]{8})$/i,
    '#id_parent_individual_case_number_confirm': /^((245|380|568|705|781|909|947|954|LEB|LB1|LB2|LBE|B6A)-[0-9]{8})$/i,
    '#id_individual_case_number': /^((245|380|568|705|781|909|947|954|LEB|LB1|LB2|LBE|B6A)-[0-9]{8})$/i,
    '#id_individual_case_number_confirm': /^((245|380|568|705|781|909|947|954|LEB|LB1|LB2|LBE|B6A)-[0-9]{8})$/i,
    '#id_recorded_number': /^((?:245|380|568|705|781|909|947|954|LEB|LB1|LB2|LBE|B6A)-[0-9]{2}[C-](?:\d{5}|\d{6})|LB-\d{3}-\d{6}|\d{7}|86A-\d{2}-\d{5})$/i,
    '#id_recorded_number_confirm': /^((?:245|380|568|705|781|909|947|954|LEB|LB1|LB2|LBE|B6A)-[0-9]{2}[C-](?:\d{5}|\d{6})|LB-\d{3}-\d{6}|\d{7}|86A-\d{2}-\d{5})$/i,
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
    $('.is-invalid').removeClass('is-invalid');
    $('.is-valid').removeClass('is-valid');
    $('.mb-3').removeClass('has-error');
    $('.step').removeClass('error');
    $('.invalid-feedback').text('');
}

function showError(selector, message) {
    var field = $(selector);
    field.addClass('is-invalid').removeClass('is-valid');
    field.closest('.mb-3').addClass('has-error');

    var stepDiv = field.closest('.step-content');
    if (stepDiv.length) {
        var stepNum = stepDiv.attr('id').split('-')[1];
        $(`.step[data-step="${stepNum}"]`).addClass('error');
    }

    // For checkboxes/radios, handle group validation
    if (field.attr('type') === 'checkbox' || field.attr('type') === 'radio') {
        var group = field.closest('.mb-3');
        var feedback = group.find('.invalid-feedback');
        if (!feedback.length) {
            feedback = $('<div class="invalid-feedback d-block"></div>');
            group.append(feedback);
        }
        feedback.text(message);
        return;
    }

    var feedback = field.siblings('.invalid-feedback');
    if (!feedback.length) {
        feedback = $('<div class="invalid-feedback"></div>');
        field.after(feedback);
    }
    feedback.text(message);
}

function showSuccess(selector) {
    var field = $(selector);
    if (field.val() && !field.hasClass('is-invalid')) {
        field.addClass('is-valid').removeClass('is-invalid');
        field.closest('.mb-3').removeClass('has-error');

        var stepDiv = field.closest('.step-content');
        if (stepDiv.length) {
            var stepNum = stepDiv.attr('id').split('-')[1];
            if ($(`#step-${stepNum}`).find('.is-invalid').length === 0) {
                $(`.step[data-step="${stepNum}"]`).removeClass('error');
            }
        }
    }
}

function validateField(field) {
    var selector = '#' + field.attr('id');
    field.removeClass('is-invalid is-valid');
    field.closest('.mb-3').removeClass('has-error');
    field.siblings('.invalid-feedback').text('');

    if (field.prop('required') && field.is(':visible') && (!field.val() || field.val().trim() === '')) {
        showError(selector, 'This field is required');
        return false;
    }

    if (regexMap[selector]) {
        var val = field.val() ? field.val().trim() : '';
        if (val && !regexMap[selector].test(val)) {
            var placeholder = field.attr('placeholder');
            var msg = translateMessage('Please enter a valid value');
            if (selector.indexOf('phone') !== -1) {
                msg = translateMessage('Please enter a valid phone number (XX-XXXXXX)');
            } else if (placeholder) {
                msg = (translateMessage('Please follow the format ')) + placeholder.replace('Format:', '').trim();
            }
            showError(selector, msg);
        }
    }
}

function validateMainForm(showModal, step) {
    if (showModal === undefined) showModal = true;

    if (isDuplicateFound) {
        if (showModal) {
            $('#child-duplication-error').fadeIn().fadeOut().fadeIn();
        }
        return false;
    }

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
        '#id_source_of_identification',
        '#id_child_living_arrangement'
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
        if (!field.val() || field.val().trim() === '') {
            showError(selector, 'This field is required');
            valid = false;
        }
    });

    // Date validation
    var year = parseInt($('#id_child_birthday_year').val(), 10) || 0;
    var month = parseInt($('#id_child_birthday_month').val(), 10) || 0;
    var day = parseInt($('#id_child_birthday_day').val(), 10) || 0;

    if (year && month && day) {
        var dt = new Date(year, month - 1, day);

    if (dt.getFullYear() !== year || dt.getMonth() !== month - 1 || dt.getDate() !== day) {
        showError('#id_child_birthday_year', 'The date is not valid.');
        valid = false;
    } else {
        var today = new Date();
        today.setHours(0, 0, 0, 0);
        dt.setHours(0, 0, 0, 0);

        if (dt > today) {
            showError('#id_child_birthday_year', 'Birth date cannot be after today.');
            valid = false;
        }
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

    // Child disability other
    var child_disability_txt = $('#id_child_disability option:selected').text();
    if ((child_disability_txt == 'Other' || child_disability_txt == 'غير ذلك') && $('#id_child_disability_other').val() === '') {
        showError('#id_child_disability_other', 'This field is required');
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
    if ($('#id_id_type').is(':visible') && (!$('#id_id_type').val() || $('#id_id_type').val().trim() === '')) {
        showError('#id_id_type', 'This field is required');
        valid = false;
    }
        if ($('#id_father_educational_level').is(':visible') && (!$('#id_father_educational_level').val() || $('#id_father_educational_level').val().trim() === '')) {
            showError('#id_father_educational_level', 'This field is required');
            valid = false;
        }
        if ($('#id_mother_educational_level').is(':visible') && (!$('#id_mother_educational_level').val() || $('#id_mother_educational_level').val().trim() === '')) {
            showError('#id_mother_educational_level', 'This field is required');
            valid = false;
        }
        var first_phone = $('#id_first_phone_number').val() ? $('#id_first_phone_number').val().trim() : '';
        var first_phone_confirm = $('#id_first_phone_number_confirm').val() ? $('#id_first_phone_number_confirm').val().trim() : '';
        if ($('#id_first_phone_owner').is(':visible') && (!$('#id_first_phone_owner').val() || $('#id_first_phone_owner').val().trim() === '')) {
            showError('#id_first_phone_owner', 'This field is required');
            valid = false;
        }
        if ($('#id_first_phone_number').is(':visible') && first_phone === '') {
            showError('#id_first_phone_number', 'This field is required');
            valid = false;
        }
        if ($('#id_first_phone_number_confirm').is(':visible') && first_phone_confirm === '') {
            showError('#id_first_phone_number_confirm', 'This field is required');
            valid = false;
        }
        if (first_phone !== first_phone_confirm) {
            showError('#id_first_phone_number_confirm', 'The phone numbers are not matched');
            valid = false;
        }
        var second_phone = $('#id_second_phone_number').val() ? $('#id_second_phone_number').val().trim() : '';
        var second_phone_confirm = $('#id_second_phone_number_confirm').val() ? $('#id_second_phone_number_confirm').val().trim() : '';
        if (second_phone !== second_phone_confirm) {
            showError('#id_second_phone_number_confirm', 'The phone numbers are not matched');
            valid = false;
        }
        var main_caregiver = $('#id_main_caregiver').val();
        if ($('#id_main_caregiver').is(':visible') && (!main_caregiver || main_caregiver.trim() === '')) {
            showError('#id_main_caregiver', 'This field is required');
            valid = false;
        }
        if ($('#id_main_caregiver_other').is(':visible') && main_caregiver == 'Other' && (!$('#id_main_caregiver_other').val() || $('#id_main_caregiver_other').val().trim() === '')) {
            showError('#id_main_caregiver_other', 'This field is required');
            valid = false;
        }
        if ($('#id_main_caregiver_nationality_other').is(':visible') && $('#id_main_caregiver_nationality').val() == '6' && (!$('#id_main_caregiver_nationality_other').val() || $('#id_main_caregiver_nationality_other').val().trim() === '')) {
            showError('#id_main_caregiver_nationality_other', 'This field is required');
            valid = false;
        }
        if ($('#id_children_number_under18').is(':visible') && (!$('#id_children_number_under18').val() || $('#id_children_number_under18').val().trim() === '')) {
            showError('#id_children_number_under18', 'This field is required');
            valid = false;
        }
        if ($('#id_caregiver_first_name').is(':visible') && (!$('#id_caregiver_first_name').val() || $('#id_caregiver_first_name').val().trim() === '')) {
            showError('#id_caregiver_first_name', 'This field is required');
            valid = false;
        }
        if ($('#id_caregiver_middle_name').is(':visible') && (!$('#id_caregiver_middle_name').val() || $('#id_caregiver_middle_name').val().trim() === '')) {
            showError('#id_caregiver_middle_name', 'This field is required');
            valid = false;
        }
        if ($('#id_caregiver_last_name').is(':visible') && (!$('#id_caregiver_last_name').val() || $('#id_caregiver_last_name').val().trim() === '')) {
            showError('#id_caregiver_last_name', 'This field is required');
            valid = false;
        }
        if ($('#id_caregiver_mother_name').is(':visible') && (!$('#id_caregiver_mother_name').val() || $('#id_caregiver_mother_name').val().trim() === '')) {
            showError('#id_caregiver_mother_name', 'This field is required');
            valid = false;
        }
        var have_labour = $('#id_have_labour').val();
        if ($('#id_have_labour').is(':visible') && (!have_labour || have_labour.trim() === '')) {
            showError('#id_have_labour', 'This field is required');
            valid = false;
        }
        if (have_labour && have_labour != 'No') {
            if ($('#id_labour_type').is(':visible') && (!$('#id_labour_type').val() || $('#id_labour_type').val().trim() === '')) {
                showError('#id_labour_type', 'This field is required');
                valid = false;
            } else if ($('#id_labour_type_specify').is(':visible') && $('#id_labour_type').val() == 'Other services' && (!$('#id_labour_type_specify').val() || $('#id_labour_type_specify').val().trim() === '')) {
                showError('#id_labour_type_specify', 'This field is required');
                valid = false;
            }
            if ($('#id_labour_hours').is(':visible') && (!$('#id_labour_hours').val() || $('#id_labour_hours').val().trim() === '')) {
                showError('#id_labour_hours', 'This field is required');
                valid = false;
            }
            if ($('#id_labour_weekly_income').is(':visible') && (!$('#id_labour_weekly_income').val() || $('#id_labour_weekly_income').val().trim() === '')) {
                showError('#id_labour_weekly_income', 'This field is required');
                valid = false;
            }
            if ($('input[name="labour_condition"]:checked').length === 0) {
                showError('input[name="labour_condition"]:first', 'This field is required');
                valid = false;
            }
        }
        var id_type = $('#id_id_type').val();
        var case_number = $('#id_case_number').val() ? $('#id_case_number').val().trim() : '';
        var case_confirm = $('#id_case_number_confirm').val() ? $('#id_case_number_confirm').val().trim() : '';
        var parent_case = $('#id_parent_individual_case_number').val() ? $('#id_parent_individual_case_number').val().trim() : '';
        var parent_case_confirm = $('#id_parent_individual_case_number_confirm').val() ? $('#id_parent_individual_case_number_confirm').val().trim() : '';
        var individual_case = $('#id_individual_case_number').val() ? $('#id_individual_case_number').val().trim() : '';
        var individual_case_confirm = $('#id_individual_case_number_confirm').val() ? $('#id_individual_case_number_confirm').val().trim() : '';
        var recorded = $('#id_recorded_number').val() ? $('#id_recorded_number').val().trim() : '';
        var recorded_confirm = $('#id_recorded_number_confirm').val() ? $('#id_recorded_number_confirm').val().trim() : '';
        var parent_syrian = $('#id_parent_syrian_national_number').val() ? $('#id_parent_syrian_national_number').val().trim() : '';
        var parent_syrian_confirm = $('#id_parent_syrian_national_number_confirm').val() ? $('#id_parent_syrian_national_number_confirm').val().trim() : '';
        var syrian = $('#id_syrian_national_number').val() ? $('#id_syrian_national_number').val().trim() : '';
        var syrian_confirm = $('#id_syrian_national_number_confirm').val() ? $('#id_syrian_national_number_confirm').val().trim() : '';
        var parent_sop = $('#id_parent_sop_national_number').val() ? $('#id_parent_sop_national_number').val().trim() : '';
        var parent_sop_confirm = $('#id_parent_sop_national_number_confirm').val() ? $('#id_parent_sop_national_number_confirm').val().trim() : '';
        var sop = $('#id_sop_national_number').val() ? $('#id_sop_national_number').val().trim() : '';
        var sop_confirm = $('#id_sop_national_number_confirm').val() ? $('#id_sop_national_number_confirm').val().trim() : '';
        var parent_nat = $('#id_parent_national_number').val() ? $('#id_parent_national_number').val().trim() : '';
        var parent_nat_confirm = $('#id_parent_national_number_confirm').val() ? $('#id_parent_national_number_confirm').val().trim() : '';
        var nat = $('#id_national_number').val() ? $('#id_national_number').val().trim() : '';
        var nat_confirm = $('#id_national_number_confirm').val() ? $('#id_national_number_confirm').val().trim() : '';
        var parent_other = $('#id_parent_other_number').val() ? $('#id_parent_other_number').val().trim() : '';
        var parent_other_confirm = $('#id_parent_other_number_confirm').val() ? $('#id_parent_other_number_confirm').val().trim() : '';
        var other = $('#id_other_number').val() ? $('#id_other_number').val().trim() : '';
        var other_confirm = $('#id_other_number_confirm').val() ? $('#id_other_number_confirm').val().trim() : '';
        var parent_extract = $('#id_parent_extract_record').val() ? $('#id_parent_extract_record').val().trim() : '';
        var parent_extract_confirm = $('#id_parent_extract_record_confirm').val() ? $('#id_parent_extract_record_confirm').val().trim() : '';

        Object.keys(regexMap).forEach(function(selector) {
            var field = $(selector);
            if (!field.is(':visible')) return;
            var val = field.val() ? field.val().trim() : '';
            if (val && !regexMap[selector].test(val)) {
                var placeholder = $(selector).attr('placeholder');
                var msg = translateMessage('Please enter a valid value');
                if (selector.indexOf('phone') !== -1) {
                    msg = translateMessage('Please enter a valid phone number (XX-XXXXXX)');
                } else if (placeholder) {
                    msg = (translateMessage('Please follow the format ')) + placeholder.replace('Format:', '').trim();
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
            if ($('#id_case_number').is(':visible') && case_number === '') {
                showError('#id_case_number', 'This field is required');
                valid = false;
            }
            if ($('#id_case_number_confirm').is(':visible') && case_number.toLowerCase() !== case_confirm.toLowerCase()) {
                showError('#id_case_number_confirm', 'The case numbers are not matched');
                valid = false;
            }
            if (parent_case.toLowerCase() !== parent_case_confirm.toLowerCase()) {
                showError('#id_parent_individual_case_number_confirm', 'The individual case numbers are not matched');
                valid = false;
            }
            if (individual_case.toLowerCase() !== individual_case_confirm.toLowerCase()) {
                showError('#id_individual_case_number_confirm', 'The individual case numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '2') {
            if (recorded === '') {
                showError('#id_recorded_number', 'This field is required');
                valid = false;
            }
            if (recorded.toLowerCase() !== recorded_confirm.toLowerCase()) {
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

        if (!$('#id_caregiver_mother_name').val() || $('#id_caregiver_mother_name').val().trim() === '') {
            showError('#id_caregiver_mother_name', 'This field is required');
            valid = false;
        }
        if (!$('#id_child_living_arrangement').val() || $('#id_child_living_arrangement').val().trim() === '') {
            showError('#id_child_living_arrangement', 'This field is required');
            valid = false;
        }

    if (showModal && !valid) {
        var missingByStep = {};
        $('.is-invalid:visible').each(function() {
            var field = $(this);
            var stepDiv = field.closest('.step-content');
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
        if (!validateMainForm(true)) {
            e.preventDefault();
        }
    });

    $('input, select').on('change input blur', function() {
        var $field = $(this);
        validateField($field);
        if (!$field.hasClass('is-invalid')) {
            showSuccess($field);
        }
        // Don't auto-validate entire form on every keypress to avoid premature step-error modals
        // Just validate current field
    });

    // Handle wizard specific validation on step change
    window.validateCurrentStep = function(step) {
        return validateMainForm(true, step);
    };


    $('#formErrorModal').on('hidden.bs.modal', function(){
        $('#formErrorModal #swal2-content').text(translateMessage('Please check the form mandatory fields.'));
    });
});
