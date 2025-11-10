/**
 * Created by ali on 7/22/17.
 */

var arabic_fields = "#id_student_first_name, #id_student_father_name, #id_student_last_name, #id_student_mother_fullname, input#id_location," +
    " #id_caretaker_mother_name, #id_caretaker_last_name, #id_caretaker_middle_name, #id_caretaker_first_name";
var protocol = window.location.protocol;
var host = protocol+window.location.host;
var moved_student_path = host+'/api/logging-student-move/';
var current_school = null;
var eligibility_msg = '';
var min_age_restriction_msg = '';
var min_age_limit_msg = '';
var max_age_limit_msg = '';

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

    check_duplicate_registration();

    if($(document).find('#id_registration_date').length == 1) {
        $('#id_registration_date').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_signature_cert_date').length == 1) {
        $('#id_signature_cert_date').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_first_attendance_date').length == 1) {
        $('#id_first_attendance_date').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_miss_school_date').length == 1) {
        $('#id_miss_school_date').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_round_start_date').length == 1) {
        $('#id_round_start_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    if($(document).find('#id_referral_date_1').length == 1) {
        $('#id_referral_date_1').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_confirmation_date_1').length == 1) {
        $('#id_confirmation_date_1').datepicker({dateFormat: "yy-mm-dd"});
    }

    if($(document).find('#id_referral_date_2').length == 1) {
        $('#id_referral_date_2').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_confirmation_date_2').length == 1) {
        $('#id_confirmation_date_2').datepicker({dateFormat: "yy-mm-dd"});
    }

    if($(document).find('#id_referral_date_3').length == 1) {
        $('#id_referral_date_3').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_confirmation_date_3').length == 1) {
        $('#id_confirmation_date_3').datepicker({dateFormat: "yy-mm-dd"});
    }

    if($(document).find('#id_followup_call_date_1').length == 1) {
        $('#id_followup_call_date_1').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_followup_call_date_2').length == 1) {
        $('#id_followup_call_date_2').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_followup_visit_date_1').length == 1) {
        $('#id_followup_visit_date_1').datepicker({dateFormat: "yy-mm-dd"});
    }


    $(document).on('change', 'select#id_round', function () {
        new_registry = $('#id_new_registry').val();
        if (new_registry == 'no') {
            duplicate_search('student id');
            duplicate_search_student_name();
        }
    });

    $(document).on('change', 'input#id_student_first_name', function () {
        duplicate_search_student_name();
    });

    $(document).on('change', 'input#id_student_father_name', function () {
        duplicate_search_student_name();
    });

    $(document).on('change', 'input#id_student_last_name', function () {
        duplicate_search_student_name();
    });


    $(document).on('change', 'input#id_case_number, ' +
        'input#id_recorded_number, ' +
        'input#id_parent_syrian_national_number, ' +
        'input#id_parent_sop_national_number, ' +
        'input#id_parent_national_number, ' +
        'input#id_parent_other_number', function () {

        duplicate_search('id');

    });

    $(document).on('change', 'input#id_phone_number', function() {
        var student_first_name= $('#id_student_first_name').val();
        // var student_father_name= $('#id_student_father_name').val();
        var phone_number= $('#id_phone_number').val();

        if (student_first_name!='' && phone_number!='' )
        {
            duplicate_search('phone');

        }
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
    $(document).on('change', 'select#id_student_nationality', function(){
        reorganizeForm();
    });
    $(document).on('change', 'select#id_have_labour_single_selection', function(){
        reorganizeForm();
    });
    $(document).on('change', 'select#id_labour_weekly_income', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_student_family_status', function(){
        family_status_single();
    });
    $(document).on('click', 'input[name=student_have_children]', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_new_registry', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_miss_school', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_main_caregiver', function(){
        var main_caregiver = $('select#id_main_caregiver').val();

        $('div#div_id_other_caregiver_relationship').addClass('d-none');
        $('#span_other_caregiver_relationship').addClass('d-none');

        if(main_caregiver == 'father'){
            var student_father_name = $('#id_student_father_name').val();
            var student_last_name = $('#id_student_last_name').val();
            $('#id_caretaker_first_name').val(student_father_name);
            $('#id_caretaker_last_name').val(student_last_name);
        }
        else if(main_caregiver == 'mother'){
            var student_mother_name = $('#id_student_mother_fullname').val();
            $('#id_caretaker_mother_name').val(student_mother_name);
        }

        else if(main_caregiver == 'other'){
            $('div#div_id_other_caregiver_relationship').removeClass('d-none');
            $('#span_other_caregiver_relationship').removeClass('d-none');

            $('#id_caretaker_first_name').val('');
            $('#id_caretaker_last_name').val('');
        }
        else {
            $('#id_caretaker_first_name').val('');
            $('#id_caretaker_last_name').val('');
        }
    });

    $(document).on('change', 'select#id_grade_registration', function(){
        reorganize_pre_assessment();
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


        if($(this).val() != 'Child have no ID'){

            return true;
        }
        if(confirm($(this).attr('translation'))) {
            $('#id_no_child_id_confirmation').val('confirmed');
        }else{
            $('#id_id_type').val('');
            $('#id_no_child_id_confirmation').val('');
        }
    });

    $(document).on('change', '#id_parent_id_type', function(){
        reorganizeForm();
        if($(this).val() != 'Parent have no ID'){

            return true;
        }
        if(confirm($(this).attr('translation'))) {
            $('#id_no_parent_id_confirmation').val('confirmed');
        }else{
            $('#id_parent_id_type').val('');
            $('#id_no_parent_id_confirmation').val('');
        }
    });

    if($(document).find('.moving-date-input').length >= 1) {
        $('.moving-date-input').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('.dropout-date-input').length >= 1) {
        $('.dropout-date-input').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('.justify-date-input').length >= 1) {
        $('.justify-date-input').datepicker({dateFormat: "yy-mm-dd"});
    }

    $("td[class='student.first_name']").addClass('font-bolder');
    $("td[class='student.father_name']").addClass('font-bolder');
    $("td[class='student.last_name']").addClass('font-bolder');

    reorganizeForm();
    reorganize_pre_assessment();


    $(document).on('change', 'select#id_level', function(){

         if($(document).find('#id_exam_result_arabic').length == 1) {
             var max_value = 30;
             var value = $('select#id_level').val();
             if(value == 4 || value == 5 || value == 6){
                 max_value = 60;
             }
             if(value == 7 || value == 8 || value == 9){
                 max_value = 90;
             }
             $('#id_exam_result_arabic, #id_exam_result_language, #id_exam_result_math, #id_exam_result_science').attr('max', max_value);
         }
    });

    /* Using Combobox select elements */
    $(document).find('select#id_school, select#id_registered_in_school, select#id_search_school, select#id_last_school')
                .combobox()
                .end();


    $(document).on('change', 'select#id_site', function(){
         reorganizeForm();
    });

    $(document).on('change', 'select#id_gender_participate', function(){
         reorganizeForm();
    });

    $(document).on('change', 'select#id_source_of_identification', function(){
         reorganizeForm();
    });

    $(document).on('change', 'select#id_follow_up_done', function(){
         reorganizeForm();
    });

    $(document).on('change', 'select#id_covid_parents_message', function(){
         reorganizeForm();
    });

    $(document).on('change', 'select#id_covid_message', function(){
         reorganizeForm();
    });

    $(document).on('change', 'select#id_remote_learning', function(){
         reorganizeForm();
    });

    $(document).on('change', 'select#id_remote_learning_reasons_not_engaged', function(){
         reorganizeForm();
    });

    $(document).on('change', 'select#id_labours_single_selection', function(){
         reorganizeForm();
    });

    $(document).on('change', 'select#id_main_caregiver_nationality', function(){

        var nationality = $('select#id_main_caregiver_nationality').val();
        $('div#div_id_main_caregiver_nationality_other').addClass('d-none');
        $('#span_main_caregiver_nationality_other').addClass('d-none');

        if(nationality == 6){
            $('div#div_id_main_caregiver_nationality_other').removeClass('d-none');
            $('#span_main_caregiver_nationality_other').removeClass('d-none');
        }
        else {
            $('#id_main_caregiver_nationality_other').val('');
        }
    });

    $(document).on('change', 'select#id_classroom, select#id_student_birthday_day, select#id_student_birthday_month, select#id_student_birthday_year', function(){
         verify_age_level();
    });

    $(document).on('change', 'select#id_student_registered_in_unhcr', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_cycle', function(){
        reorganizeForm();
    });
    $(document).on('change', 'select#id_student_outreached', function(){
        reorganizeForm();
    });
    $(document).on('change', 'select#id_have_barcode', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_participation', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_follow_up_type', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_attended_arabic', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_attended_english', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_attended_math', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_attended_social', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_attended_psychomotor', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_attended_science', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_attended_artistic', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_attended_biology', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_attended_chemistry', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_attended_physics', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_parent_attended', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_barriers_single', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_test_done', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_followup_session_attended', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_pss_session_modality', function(){
        reorganize_pre_assessment();
    });

    $(document).on('change', 'select#id_covid_session_attended', function(){
        reorganize_pre_assessment();
    });


    $(document).on('blur', arabic_fields, function(){
        checkArabicOnly($(this));
    });

    $(document).on('blur', '#id_student_id_number', function(){
        var result = true;
        var type = $('#id_student_id_type').val();
        var value = $(this).val();
        if(type == 1){
            result = check_unhcr_number(value);
        }
        if(type == 3) {
            result = check_national_id(value);
        }
        if(!result){
            $(this).val('');
        }
    });

    $(document).on('click', '.moved-button', function(){
        var item = $(this);
        var itemscope = item.attr('itemscope');
        if(confirm($(this).attr('translation'))) {

            $('.moving-date-block').addClass('d-none');
            $('#moving_date_block_'+itemscope).removeClass('d-none');
        }
    });
    $(document).on('click', '.cancel-moved-button', function(){
        var itemscope = $(this).attr('itemscope');
        $('#moving_date_block_'+itemscope).addClass('d-none');
        $('#moved_button_'+itemscope).removeClass('d-none');
    });
    $(document).on('click', '.save-moved-button', function(){
        var item = $(this);
        var itemscope = item.attr('itemscope');
        if($('#moving_date_'+itemscope).val()) {
            moved_student(item.attr('itemscope'), $('#moving_date_'+itemscope).val());
            item.parents('tr').remove();
        }
    });

    $(document).on('click', '.dropout-button', function(){
        var item = $(this);
        var itemscope = item.attr('itemscope');
        if(confirm($(this).attr('translation'))) {

            $('.dropout-date-block').addClass('d-none');
            $('#dropout_date_block_'+itemscope).removeClass('d-none');
        }
    });
    $(document).on('click', '.cancel-dropout-button', function(){
        var itemscope = $(this).attr('itemscope');
        $('#dropout_date_block_'+itemscope).addClass('d-none');
        $('#dropout_button_'+itemscope).removeClass('d-none');
    });
    $(document).on('click', '.save-dropout-button', function(){
        var item = $(this);
        var itemscope = item.attr('itemscope');
        if($('#dropout_date_'+itemscope).val()) {
            dropout_student_enrollment(item.attr('itemscope'), $('#dropout_date_'+itemscope).val());
            item.parents('tr').remove();
        }
    });


   $(document).on('click', '.justify-button', function(){
        var item = $(this);
        var itemscope = item.attr('itemscope');
        if(confirm($(this).attr('translation'))) {
            $('.justify-date-block').addClass('d-none');
            $('#justify_date_block_'+itemscope).removeClass('d-none');
            var itemscope = item.attr('itemscope');
            justify_student_enrollment(item.attr('itemscope'));
        }
    });

    $(document).on('click', '.detach-button', function(){
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            var callback = function(){
                item.parents('tr').remove();
            };
            patch_registration(item, callback());
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

    if($(document).find('#id_search_student').length == 1) {

        $("#id_search_student").autocomplete({
            source: function (request, response) {
                var school = $('#id_search_school').val();
                if (school == '') { school = 0; }

                var school_type = $('#id_school_type').val();
                if (school_type == undefined){
                    school_type = 'alp';
                }

                $.ajax({
                    url: '/api/students-search/?school=' + school + '&school_type=' + school_type,
                    dataType: "json",
                    data: {
                        term: request.term
                    },
                    success: function (data) {
                       if(!data.length){
                            var result = [{ error: 'No matches found',  value: response.term }];
                            response(result);
                         }else{
                            response(data);

                        }
                    }
                });
            },
            minLength: 3,
            select: function (event, ui) {
                if(ui.item.error) {
                    return false;
                }
                var registry_id = 0;
                var eligibility = true;
                var school_type = $('#id_school_type').val();
                if(school_type == undefined || school_type == 'alp'){
                    registry_id = ui.item.registration.id;
                    if(school_type == 'alp') {
                        var refer_to_level = ui.item.registration.refer_to_level;
                        if (!$.inArray(refer_to_level, [1, 10, 11, 12, 13, 14, 15, 16, 17])) {
                            if (confirm(eligibility_msg)) {
                                eligibility = false;
                            } else {
                                return false;
                            }
                        }
                        log_student_program_move(ui.item.registration, eligibility);
                    }
                }else{
                    registry_id = ui.item.enrollment.id;
                }
                var params = {
                    enrollment_id: registry_id,
                    new_registry: $('select#id_new_registry').val(),
                    student_outreached: $('select#id_student_outreached').val(),
                    have_barcode: $('select#id_have_barcode').val(),
                    school_type: school_type
                };
                var str = '?'+jQuery.param( params );

                window_location($(document).find('form').attr('action')+str);
//                window.location = $(document).find('form').attr('action')+str;
                return false;
            }
        }).autocomplete("instance")._renderMenu = function (ul, items) {
            var that = this;
            $.each(items, function (index, item) {
                that._renderItemData(ul, item);
            });
            $(ul).find("li:odd").addClass("odd");
        };

        $("#id_search_student").autocomplete("instance")._renderItem = function (ul, item) {
            if(item.error) {
                return $("<li>").append('<div class="error">No result found</div>').appendTo(ul);
            }
            var registry = item.enrollment;
            if(registry){
                var education_year_name = registry.education_year_name;
            }
            if($('#id_school_type').val() == undefined || $('#id_school_type').val() == 'alp'){
                registry = item.registration;
                education_year_name = registry.alp_round_name;
            }

            return $("<li>")
                .append("<div style='border: 1px solid;'>"
                    + "<b>Base Data:</b> " + item.full_name + " - " + item.mother_fullname + " - " + item.id_number
                    + "<br/> <b>Gender - Birthday:</b> " + item.sex + " - " + item.birthday
                    + "<br/> <b>Last education year:</b> " + education_year_name
                    + "<br/> <b>Last education school:</b> " + registry.school_name + " - " + registry.school_number
                    + "<br/> <b>Class / Section:</b> " + registry.classroom_name + " / " + registry.section_name
                    + "</div>")
                .appendTo(ul);
        };
    }

    if($(document).find('#id_search_clm_student').length == 1) {

        $("#id_search_clm_student").autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: '/clm/search-clm-child/?clm_type='+$('#id_clm_type').val(),
                    dataType: "json",
                    data: {
                        term: request.term
                    },
                    success: function (data) {
                       var result = JSON.parse(data.result);
                       if(!result.length){
                            var result = [{ error: 'No matches found',  value: response.term }];
                            response(result);
                         }else{
                            response(result);
                        }
                    }
                });
            },
            minLength: 3,
            select: function (event, ui) {
                if(ui.item.error) {
                    return false;
                }
                var params = {
                    enrollment_id: ui.item.id,
                    new_registry: $('select#id_new_registry').val(),
                    student_outreached: $('select#id_student_outreached').val(),
                    have_barcode: $('select#id_have_barcode').val()
                };
                var str = '?'+jQuery.param( params );

                window_location($(document).find('form').attr('action')+str);
//                window.location = $(document).find('form').attr('action')+str;
                return false;
            }
        }).autocomplete("instance")._renderMenu = function (ul, items) {
            var that = this;
            $.each(items, function (index, item) {
                that._renderItemData(ul, item);
            });
            $(ul).find("li:odd").addClass("odd");
        };

        $("#id_search_clm_student").autocomplete("instance")._renderItem = function (ul, item) {
            if(item.error) {
                return $("<li>").append('<div class="error">No result found</div>').appendTo(ul);
            }
            var full_name = item.student__first_name+" "+item.student__father_name+" "+item.student__last_name;
            var student_birthday = item.student__birthday_day+"/"+item.student__birthday_month+"/"+item.student__birthday_year;
            return $("<li>")
                .append("<div style='border: 1px solid;'>"
                    + "<b>Base Data:</b> " + full_name + " - " + item.student__mother_fullname
                    + "<br/> <b>Gender - Birthday:</b> " + item.student__sex + " - " + student_birthday
                     + "<br/> <b>Internal number:</b> " + item.internal_number
                     + "<br/> <b>Round:</b> " + item.round__name
                    + "</div>")
                .appendTo(ul);
        };
    }

    if($(document).find('#id_search_barcode').length == 1) {

        $("#id_search_barcode").autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: '/api/child/',
                    dataType: "json",
                    data: {
                        term: request.term
                    },
                    success: function (data) {
                       if(!data.length){
                            var result = [{ error: 'No matches found',  value: response.term }];
                            response(result);
                         }else{
                            response(data);
                        }
                    }
                });
            },
            minLength: 10,
            select: function (event, ui) {
                if(ui.item.error) {
                    return false;
                }
                var params = {
                    child_id: ui.item.child_id,
                    new_registry: $('select#id_new_registry').val(),
                    student_outreached: $('select#id_student_outreached').val(),
                    have_barcode: $('select#id_have_barcode').val()
                };
                var str = '?'+jQuery.param( params );

                window_location($(document).find('form').attr('action')+str);
//                window.location = $(document).find('form').attr('action')+str;
                return false;
            }
        }).autocomplete("instance")._renderMenu = function (ul, items) {
            var that = this;
            $.each(items, function (index, item) {
                that._renderItemData(ul, item);
            });
            $(ul).find("li:odd").addClass("odd");
        };

        $("#id_search_barcode").autocomplete("instance")._renderItem = function (ul, item) {
            if(item.error) {
                return $("<li>").append('<div class="error">No result found</div>').appendTo(ul);
            }
            return $("<li>")
                .append("<div style='border: 1px solid;'>"
                    + "<b>Base Data:</b> " + item.student_full_name + " - " + item.student_mother_fullname + " - " + item.student_id_number
                    + "<br/> <b>Gender - Birthday:</b> " + item.student_sex + " - " + item.student_birthday
                    + "</div>")
                .appendTo(ul);
        };
    }

    if($(document).find('#id_outreach_barcode').length == 1) {

        $("#id_outreach_barcode").autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: '/api/child/',
                    dataType: "json",
                    data: {
                        term: request.term
                    },
                    success: function (data) {
                       if(!data.length){
                            var result = [{ error: 'No matches found',  value: response.term }];
                            response(result);
                         }else{
                            response(data);
                        }
                    }
                });
            },
            minLength: 10,
            select: function (event, ui) {
                if(ui.item.error) {
                    return false;
                }
                $('#id_outreach_barcode').val(ui.item.barcode_subset);
                return false;
            }
        }).autocomplete("instance")._renderMenu = function (ul, items) {
            var that = this;
            $.each(items, function (index, item) {
                that._renderItemData(ul, item);
            });
            $(ul).find("li:odd").addClass("odd");
        };

        $("#id_outreach_barcode").autocomplete("instance")._renderItem = function (ul, item) {
            if(item.error) {
                return $("<li>").append('<div class="error">No result found</div>').appendTo(ul);
            }
            return $("<li>")
                .append("<div style='border: 1px solid;'>"
                    + "<b>Base Data:</b> " + item.student_full_name + " - " + item.stduent_mother_fullname + " - " + item.student_id_number
                    + "<br/> <b>Gender - Birthday:</b> " + item.student_sex + " - " + item.student_birthday
                    + "</div>")
                .appendTo(ul);
        };
    }

    if($(document).find('#search_moved_student').length == 1) {

        $("#search_moved_student").autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: '/api/logging-student-move/',
                    dataType: "json",
                    data: {
                        term: request.term
                    },
                    success: function (data) {
                       if(!data.length){
                            var result = [{ error: 'No matches found',  value: response.term }];
                            response(result);
                         }else{
                            response(data);
                        }
                    }
                });
            },
            minLength: 3,
            select: function (event, ui) {
                if(ui.item.error) {
                    return false;
                }
                $("#search_moved_student").val('');
                window_location('/enrollments/moved/' + ui.item.enrolment_id + '/' + ui.item.id);
//                window.location = '/enrollments/moved/' + ui.item.enrolment_id + '/' + ui.item.id;
                return false;
            }
        }).autocomplete("instance")._renderMenu = function (ul, items) {
            var that = this;
            $.each(items, function (index, item) {
                that._renderItemData(ul, item);
            });
            $(ul).find("li:odd").addClass("odd");
        };

        $("#search_moved_student").autocomplete("instance")._renderItem = function (ul, item) {
            if(item.error) {
                return $("<li>").append('<div class="error">No result found</div>').appendTo(ul);
            }
            return $("<li>")
                .append("<div style='border: 1px solid;'>" + item.student_full_name + " - " + item.student_mother_fullname + " (" + item.student_sex + " - " + item.student_age + ") "
                    + "<br> Current situation: " + item.school_name + " - " + item.school_number + " / " + item.classroom_name + " / " + item.section_name
                    + "</div>")
                .appendTo(ul);
        };
    }

    pageScripts();

        /* Ajax page load settings */
        $(document).on('pjax:end', pageScripts);
        if (sessionStorage.getItem("pjax-enabled") === "0") {
            return;
        }
        // Comment it to disable Ajax Page load
        // $(document).pjax('a', '.content-wrap', {fragment: '.content-wrap'});

        $(document).on('pjax:beforeReplace', function() {
            $('.content-wrap').css('opacity', '0.1');
            setTimeout(function() {
                $('.content-wrap').fadeTo('100', '1');
            }, 1);
        });
});

function pageScripts() {
    /* Magnific Popup */
    $('.image-link').magnificPopup({
        type: 'image',
        gallery: {
            enabled: true
        }
    });
}

function urlParam(name){
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	if (results && results.length){
        return results[1] || 0;
    }
    return 0;
}

function check_duplicate_registration()
{
    enrollment_id = $('#id_enrollment_id').val();
    partner_name = $('#id_partner_name').val();
    id_round = $('#id_round').val();

    if (enrollment_id > 0 && id_round > 0)
    {
        if (isAddPage() && ($('.errorlist').length == 0))
        {
            showModal("The child already exists with the partner " + partner_name);
            $(':input[type="submit"][name="save_add_another"]').prop('disabled', true);
            $(':input[type="submit"][name="save"]').prop('disabled', true);
        }
        else
        {
            $(':input[type="submit"][name="save_add_another"]').prop('disabled', false);
            $(':input[type="submit"][name="save"]').prop('disabled', false);
        }
    }
}
function isAddPage()
{
    var url_loc = window.location.toString();
    return (url_loc.toLowerCase().search(/^.*\/clm\/bln-add|abln-add|cbece-add|rs-add|inclusion-add|outreach-add(\*)(\?.*)?$/i)>=0);
}

function reorganizeForm()
{
    var new_registry = $('select#id_new_registry').val();
    var outreached = $('select#id_student_outreached').val();
    var have_barcode = $('select#id_have_barcode').val();
    var program_site = $('select#id_site').val();
    var registered_unhcr = $('select#id_student_registered_in_unhcr').val();
    var id_cycle = $('select#id_cycle').val();
    var id_type = $('select#id_id_type').val();
    var nationality = $('select#id_student_nationality').val();
    var family_status = $('select#id_student_family_status').val();
    var have_children = $('input[name=student_have_children]:checked').val();
    var have_labour = $('select#id_have_labour_single_selection').val();
    var labour_selection = $('select#id_labours_single_selection').val();
    var main_caregiver = $('select#id_main_caregiver').val();


    var covid_message = $('select#id_covid_message').val();
    var covid_parents_message = $('select#id_covid_parents_message').val();
    var gender_participate = $('select#id_gender_participate').val();
    var follow_up_done = $('select#id_follow_up_done').val();

    var remote_learning = $('select#id_remote_learning').val();
    var remote_learning_reasons_not_engaged = $('select#id_remote_learning_reasons_not_engaged').val();

    var source_of_identification = $('select#id_source_of_identification').val();

    var miss_school = $('select#id_miss_school').val();

    // miss_school
    $('div#div_id_miss_school_date').addClass('d-none');
    $('#span_miss_school_date').addClass('d-none');
    if(miss_school == 'yes'){
        $('#div_id_miss_school_date').removeClass('d-none');
        $('#span_miss_school_date').removeClass('d-none');
    }



    // source_of_identification
    $('div#div_id_source_of_identification_specify').addClass('d-none');
    $('#span_source_of_identification_specify').addClass('d-none');

    $('div#div_id_rims_case_number').addClass('d-none');
    $('#span_rims_case_number').addClass('d-none');


    if(source_of_identification == 'Other Sources'){
        $('#div_id_source_of_identification_specify').removeClass('d-none');
        $('#span_source_of_identification_specify').removeClass('d-none');
    }

    if(source_of_identification == 'RIMS'){
        $('#div_id_rims_case_number').removeClass('d-none');
        $('#span_rims_case_number').removeClass('d-none');
    }

    $('div#div_id_student_have_children').addClass('d-none');
    $('#span_student_have_children').addClass('d-none');
    if(family_status !='single'){
        $('div#div_id_student_have_children').removeClass('d-none');
        $('#span_student_have_children').removeClass('d-none');
    }
    else{
        $('input:radio[name=student_have_children]').filter('[value=0]').prop('checked', true);
        $('#id_student_number_children').val('');
        $('div#div_id_student_number_children').addClass('d-none');
        $('#span_student_number_children').addClass('d-none');
        $('#span_student_have_children').addClass('d-none');
    }

    $('div.child_id').addClass('d-none');

    // id_student_nationality
    $('div#div_id_other_nationality').addClass('d-none');
    $('#span_other_nationality').addClass('d-none');

    // showModal(nationality);
    if(nationality == '6'){
        $('#div_id_other_nationality').removeClass('d-none');
    $('#span_other_nationality').removeClass('d-none');
    }


    // id_covid_message
    $('div#div_id_covid_message_how_often').addClass('d-none');
    $('#span_covid_message_how_often').addClass('d-none');
    if(covid_message == 'yes'){
        $('div#div_id_covid_message_how_often').removeClass('d-none');
        $('#span_covid_message_how_often').removeClass('d-none');
    }

    // id_covid_parents_message
    $('div#div_id_covid_parents_message_how_often').addClass('d-none');
    $('#span_covid_parents_message_how_often').addClass('d-none');
    if(covid_parents_message == 'yes'){
        $('div#div_id_covid_parents_message_how_often').removeClass('d-none');
        $('#span_covid_parents_message_how_often').removeClass('d-none');
    }

    // id_gender_participate
    $('div#div_id_gender_participate_explain').addClass('d-none');
    $('#span_gender_participate_explain').addClass('d-none');
    if(gender_participate =='no'){
        $('#div_id_gender_participate_explain').removeClass('d-none');
        $('#span_gender_participate_explain').removeClass('d-none');
    }else{
        $('#id_gender_participate_explain').val('');
    }

    // id_follow_up_done
    $('div#div_id_follow_up_done_with_who').addClass('d-none');
    $('#span_follow_up_done_with_who').addClass('d-none');
    if(follow_up_done == 'yes'){
        $('div#div_id_follow_up_done_with_who').removeClass('d-none');
        $('#span_follow_up_done_with_who').removeClass('d-none');
    }

    // remote_learning
    $('div#div_id_remote_learning_reasons_not_engaged').addClass('d-none');
    $('#span_remote_learning_reasons_not_engaged').addClass('d-none');
    if(remote_learning == 'no'){
        $('div#div_id_remote_learning_reasons_not_engaged').removeClass('d-none');
        $('#span_remote_learning_reasons_not_engaged').removeClass('d-none');
    }
    else{
        $('#id_reasons_not_engaged_other').val('');
        $('div#div_id_reasons_not_engaged_other').addClass('d-none');
        $('#span_reasons_not_engaged_other').addClass('d-none');
        $('div#div_id_remote_learning_reasons_not_engaged').addClass('d-none');
        $('#span_remote_learning_reasons_not_engaged').addClass('d-none');
    }

    // remote_learning_reasons_not_engaged
    $('div#div_id_reasons_not_engaged_other').addClass('d-none');
    $('#span_reasons_not_engaged_other').addClass('d-none');
    if(remote_learning_reasons_not_engaged == 'Other'){
        $('div#div_id_reasons_not_engaged_other').removeClass('d-none');
        $('#span_reasons_not_engaged_other').removeClass('d-none');
    }else{
        $('#id_reasons_not_engaged_other').val('');
        $('div#div_id_reasons_not_engaged_other').addClass('d-none');
        $('#span_reasons_not_engaged_other').addClass('d-none');
    }


    // have_children
    $('div#div_id_student_number_children').addClass('d-none');
    $('#span_student_number_children').addClass('d-none');
    if(have_children =='1'){
        $('div#div_id_student_number_children').removeClass('d-none');
        $('#span_student_number_children').removeClass('d-none');
    }else{
        $('#id_student_number_children').val('');
    }

    // have_labour_single_selection
     $('#labour_details_1').addClass('d-none');
     $('#labour_details_2').addClass('d-none');
    if(have_labour != 'no'){
        $('#labour_details_1').removeClass('d-none');
        $('#labour_details_2').removeClass('d-none');
    }
    else
    {
        $('#id_labours_single_selection').val('')
        $('#id_labours_other_specify').val('')
        $('#id_labour_hours').val('')
        $('#id_labour_weekly_income').val('')

    }

     // labour_selection
    $('div#div_id_labours_other_specify').addClass('d-none');
    $('#span_labours_other_specify').addClass('d-none');
    if(labour_selection =='other_many_other'){
        $('div#div_id_labours_other_specify').removeClass('d-none');
        $('#span_labours_other_specify').removeClass('d-none');
    }
    else
    {
        $('#id_labours_other_specify').val('');
    }

    if(id_type == 'UNHCR Registered'){
        $('div.child_id1').removeClass('d-none');
    }

    if(id_type == 'UNHCR Recorded'){
        $('div.child_id2').removeClass('d-none');
    }

    if(id_type == 'Lebanese national ID'){
        $('div.child_id3').removeClass('d-none');
    }

    if(id_type == 'Syrian national ID'){
        $('div.child_id4').removeClass('d-none');
    }

    if(id_type == 'Palestinian national ID'){
        $('div.child_id5').removeClass('d-none');
    }

    if(id_type == 'Other nationality'){
        $('div.child_id6').removeClass('d-none');
    }

    if(program_site == 'out_school') {
        $('div#div_id_school').parent().addClass('d-none');
        $('div#div_id_school').parent().prev().addClass('d-none');
    }else{
        $('div#div_id_school').parent().removeClass('d-none');
        $('div#div_id_school').parent().prev().removeClass('d-none');
    }


    if(main_caregiver == 'other'){
        $('div#div_id_other_caregiver_relationship').removeClass('d-none');
        $('#span_other_caregiver_relationship').removeClass('d-none');
    }
    else {
        $('div#div_id_other_caregiver_relationship').addClass('d-none');
        $('#span_other_caregiver_relationship').addClass('d-none');
        }


    if(id_cycle == '3'){
        $('option[value=graduated_to_formal_kg]').show();
        $('option[value=graduated_to_formal_level1]').show();
    }else{
        $('option[value=graduated_to_formal_kg]').hide();
        $('option[value=graduated_to_formal_level1]').hide();
    }

    if(registered_unhcr == '1') {
        $('select#id_student_id_type').val(1);
    }

    if(have_barcode == 'no'){
        $('#block_id_outreach_barcode').addClass('d-none');
        $('#block_id_outreach_barcode').prev().addClass('d-none');
    }else{
        $('#block_id_outreach_barcode').removeClass('d-none');
        $('#block_id_outreach_barcode').prev().removeClass('d-none');
    }

    $('#search_options').addClass('d-none');
    if(urlParam('child_id') || urlParam('enrollment_id') || $('#registry_block').hasClass('d-none')) {
        $('#registry_block').addClass('d-none');
        $('#register_by_barcode').addClass('d-none');
        // $('#search_options').addClass('d-none');
        return true;
    }

    if(outreached == 'no'){
        $('#have_barcode_option').addClass('d-none');
        $('#have_barcode_option').prev().addClass('d-none');
        $('select#id_have_barcode').val('no');
    }else{
        $('#have_barcode_option').removeClass('d-none');
        $('#have_barcode_option').prev().removeClass('d-none');
        // $('select#id_have_barcode').val('yes');
    }

    if(new_registry == 'yes' && outreached == 'yes' && have_barcode == 'yes'){
        $('#block_id_outreach_barcode').removeClass('d-none');
        $('#block_id_outreach_barcode').prev().removeClass('d-none');

        $('#register_by_barcode').removeClass('d-none');
        // $('#search_options').addClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }

    if(new_registry == 'yes' && outreached == 'yes' && have_barcode == 'no'){
        $('#register_by_barcode').addClass('d-none');
        // $('#search_options').addClass('d-none');
        $('.child_data').removeClass('d-none');
        return true;
    }

    if(new_registry == 'yes' && outreached == 'no'){

        $('#register_by_barcode').addClass('d-none');
        // $('#search_options').addClass('d-none');
        $('.child_data').removeClass('d-none');

        return true;
    }

    if(new_registry == 'no' && outreached == 'no'){

        $('#register_by_barcode').addClass('d-none');
        // $('#search_options').removeClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }

    if(new_registry == 'no' && outreached == 'yes' && have_barcode == 'yes'){

        $('#register_by_barcode').addClass('d-none');
        // $('#search_options').removeClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }
    if(new_registry == 'no' && outreached == 'yes' && have_barcode == 'no'){

        $('#register_by_barcode').addClass('d-none');
        // $('#search_options').removeClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }

    if(new_registry == 'no')
     // search_options
     {
        $('#search_options').removeClass('d-none');
     }

    reorganize_pre_assessment();


}



function duplicate_search_student_name()
{
    var student_first_name= $('#id_student_first_name').val();
    var student_father_name= $('#id_student_father_name').val();
    var student_last_name= $('#id_student_last_name').val();

    if (student_first_name!='' && student_father_name!='' && student_last_name!='' )
    {
        duplicate_search('student name');

    }

}


function duplicate_search(search_by) {

    if (isAddPage()) {

        var search_by = search_by
        var round = $('select#id_round').val();
        var new_registry = $('select#id_new_registry').val();
        var clm_type = $('#id_clm_type').val();
        var student_id = $('#id_student_id').val();
        var student_first_name = $('#id_student_first_name').val();
        var student_father_name = $('#id_student_father_name').val();
        var student_last_name = $('#id_student_last_name').val();
        var phone_number = $('#id_phone_number').val();
        var id_type = $('#id_id_type').val();
        var case_number = $('#id_case_number').val();
        var recorded_number = $('#id_recorded_number').val();
        var parent_syrian_national_number = $('#id_parent_syrian_national_number').val();
        var parent_sop_national_number = $('#id_parent_sop_national_number').val();
        var parent_national_number = $('#id_parent_national_number').val();
        var parent_other_number = $('#id_parent_other_number').val();


        var data = {
            search_by: search_by,
            round_id: round,
            new_registry: new_registry,
            clm_type: clm_type,
            student_id: student_id,
            student_first_name: student_first_name,
            student_father_name: student_father_name,
            student_last_name: student_last_name,
            phone_number: phone_number,
            id_type: '',
            case_number: '',
            recorded_number: '',
            parent_syrian_national_number: '',
            parent_sop_national_number: '',
            parent_national_number: '',
            parent_other_number: '',
        };

        requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        $.ajax({
            type: "POST",
            url: '/clm/search-clm-duplicate-registration/',
            data: JSON.stringify(data),
            cache: false,
            async: false,
            headers: requestHeaders,
            dataType: 'json',
            success: function (response) {
                // showModal(response.result);

                if (response.result != "") {
                    showModal("The child already exists with the partner  " + response.result);
                    $(':input[type="submit"][name="save_add_another"]').prop('disabled', true);
                    $(':input[type="submit"][name="save"]').prop('disabled', true);
                    // $('#').addClass('d-none');

                }
                else {
                    $(':input[type="submit"][name="save_add_another"]').prop('disabled', false);
                    $(':input[type="submit"][name="save"]').prop('disabled', false);
                }

                console.log(response);
            },
            error: function (response) {
                console.log(response);
            }

        });


    }

}

function family_status_single()
{
    var family_status = $('select#id_student_family_status').val();

    $('div#div_id_student_have_children').addClass('d-none');
    $('#span_student_have_children').addClass('d-none');
    if(family_status !='single'){
        $('div#div_id_student_have_children').removeClass('d-none');
        $('#span_student_have_children').removeClass('d-none');
    }
    else{
        $('input:radio[name=student_have_children]').filter('[value=0]').prop('checked', true);
        $('#id_student_number_children').val('');
        $('div#div_id_student_number_children').addClass('d-none');
        $('#span_student_number_children').addClass('d-none');
        $('#span_student_have_children').addClass('d-none');
    }
}

function reorganize_pre_assessment()
{

    var participation = $('select#id_participation').val();
    var barriers_single = $('select#id_barriers_single').val();
    var follow_up_type = $('select#id_follow_up_type').val();

    var attended_arabic = $('select#id_attended_arabic').val();
    var attended_english = $('select#id_attended_english').val();
    var attended_math = $('select#id_attended_math').val();
    var attended_social = $('select#id_attended_social').val();
    var attended_psychomotor = $('select#id_attended_psychomotor').val();

    var attended_science = $('select#id_attended_science').val();
    var attended_artistic = $('select#id_attended_artistic').val();


    var attended_biology = $('select#id_attended_biology').val();
    var attended_chemistry = $('select#id_attended_chemistry').val();
    var attended_physics = $('select#id_attended_physics').val();


    var grade_registration = $('select#id_grade_registration').val();
    // grade_registration
    $('div.grd6').addClass('d-none');
    $('div.grd7').addClass('d-none');

    if(grade_registration == '7'){
        $('div.grd7').removeClass('d-none');
    }else if(grade_registration == '8'){
        $('div.grd7').removeClass('d-none');
    }else if(grade_registration == '9'){
        $('div.grd7').removeClass('d-none');
    }
    else{
        $('div.grd6').removeClass('d-none');
        }


    var pss_session_attended = $('select#id_pss_session_attended').val();
    var covid_session_attended = $('select#id_covid_session_attended').val();
    var followup_session_attended = $('select#id_followup_session_attended').val();

    var parent_attended =  $('select#id_parent_attended').val();

    // id_participation
    $('div#div_id_barriers_single').addClass('d-none');
    $('#span_barriers_single').addClass('d-none');
    $('div#div_id_barriers_other').addClass('d-none');
    $('#span_barriers_other').addClass('d-none');
    $('#follow_up').addClass('hide');
    $('#visits').addClass('hide');



    if(participation != 'no_absence'){
        $('#div_id_barriers_single').removeClass('d-none');
        $('#span_barriers_single').removeClass('d-none');
        $('#follow_up').removeClass('hide');
        $('#visits').removeClass('hide');
        // $('input[name=follow_up_type]').val('none').checked(true);
        $('#id_phone_call_number').val('');
        $('#id_house_visit_number').val('');
        $('#id_family_visit_number').val('');
    }

    if(barriers_single == 'other'){
        $('#div_id_barriers_other').removeClass('d-none');
        $('#span_barriers_other').removeClass('d-none');
    }
    else
    {
        $('#id_barriers_other').val('');
    }

    $('div#div_id_round_complete').addClass('d-none');
    $('#span_round_complete').addClass('d-none');
    $('div.grades').addClass('d-none');

    // follow_up_type
    $('div#div_phone_call_number').addClass('d-none');
    $('div#div_house_visit_number').addClass('d-none');
    $('div#div_family_visit_number').addClass('d-none');
    if(follow_up_type == 'Phone'){
        $('div#div_phone_call_number').removeClass('d-none');

    }else if(follow_up_type == 'House visit'){
        $('div#div_house_visit_number').removeClass('d-none');

    }else if(follow_up_type == 'Family Visit') {
        $('div#div_family_visit_number').removeClass('d-none');
    }

    $('div#div_id_arabic').addClass('d-none');
    $('#span_arabic').addClass('d-none');
    $('div#div_id_modality_arabic').addClass('d-none');
    $('#span_modality_arabic').addClass('d-none');

    $('div#div_id_english').addClass('d-none');
    $('#span_english').addClass('d-none');
    $('div#div_id_modality_english').addClass('d-none');
    $('#span_modality_english').addClass('d-none');

    $('div#div_id_math').addClass('d-none');
    $('#span_math').addClass('d-none');
    $('div#div_id_modality_math').addClass('d-none');
    $('#span_modality_math').addClass('d-none');

    $('div#div_id_social_emotional').addClass('d-none');
    $('#span_social_emotional').addClass('d-none');
    $('div#div_id_modality_social').addClass('d-none');
    $('#span_modality_social').addClass('d-none');

    $('div#div_id_psychomotor').addClass('d-none');
    $('#span_psychomotor').addClass('d-none');
    $('div#div_id_modality_psychomotor').addClass('d-none');
    $('#span_modality_psychomotor').addClass('d-none');


    $('div#div_id_science').addClass('d-none');
    $('#span_science').addClass('d-none');
    $('div#div_id_modality_science').addClass('d-none');
    $('#span_modality_science').addClass('d-none');

    $('div#div_id_artistic ').addClass('d-none');
    $('#span_artistic ').addClass('d-none');
    $('div#div_id_modality_artistic ').addClass('d-none');
    $('#span_modality_artistic ').addClass('d-none');

    // attended_arabic
    if(attended_arabic == 'yes'){
        $('div#div_id_arabic').removeClass('d-none');
        $('#span_arabic').removeClass('d-none');
        $('div#div_id_modality_arabic').removeClass('d-none');
        $('#span_modality_arabic').removeClass('d-none');

    }
    else{
        $('#id_arabic').val('');
        $('select#id_modality_arabic').val("");

    }

    // attended_english
    if(attended_english == 'yes'){
        $('div#div_id_english').removeClass('d-none');
        $('#span_english').removeClass('d-none');
        $('div#div_id_modality_english').removeClass('d-none');
        $('#span_modality_english').removeClass('d-none');

    }
    else{
        $('#id_english').val('');
        $('select#id_modality_english').val("");
    }

    // attended_math
    if(attended_math == 'yes'){
        $('div#div_id_math').removeClass('d-none');
        $('#span_math').removeClass('d-none');
        $('div#div_id_modality_math').removeClass('d-none');
        $('#span_modality_math').removeClass('d-none');
    }
    else{
        $('#id_math').val('');
        $('select#id_modality_math').val("");
    }
    // attended_social
    if(attended_social == 'yes'){
        $('div#div_id_social_emotional').removeClass('d-none');
        $('#span_social_emotional').removeClass('d-none');
        $('div#div_id_modality_social').removeClass('d-none');
        $('#span_modality_social').removeClass('d-none');
    }
    else{
        $('#id_social').val('');
        $('select#id_modality_social').val("");
    }
    // attended_psychomotor
    if(attended_psychomotor == 'yes'){
        $('div#div_id_psychomotor').removeClass('d-none');
        $('#span_psychomotor').removeClass('d-none');
        $('div#div_id_modality_psychomotor').removeClass('d-none');
        $('#span_modality_psychomotor').removeClass('d-none');
    }
    else{
        $('#id_psychomotor').val('');
        $('select#id_modality_psychomotor').val("");
    }

    // attended_science,
    if(attended_science == 'yes'){
        $('div#div_id_science').removeClass('d-none');
        $('#span_science').removeClass('d-none');
        $('div#div_id_modality_science').removeClass('d-none');
        $('#span_modality_science').removeClass('d-none');
    }
    else{
        $('#id_science').val('');
        $('select#id_modality_science').val("");
    }

    // attended_artistic
    if(attended_artistic == 'yes'){
        $('div#div_id_artistic').removeClass('d-none');
        $('#span_artistic').removeClass('d-none');
        $('div#div_id_modality_artistic').removeClass('d-none');
        $('#span_modality_artistic').removeClass('d-none');
    }
    else{
        $('#id_artistic').val('');
        $('select#id_modality_artistic').val("");
    }

    // attended_biology
    if(attended_biology == 'yes'){
        $('div#div_id_biology').removeClass('d-none');
        $('#span_biology').removeClass('d-none');
        $('div#div_id_modality_biology').removeClass('d-none');
        $('#span_modality_biology').removeClass('d-none');
    }
    else{
        $('#id_biology').val('');
        $('select#id_modality_biology').val("");
    }

    // attended_chemistry
    if(attended_chemistry == 'yes'){
        $('div#div_id_chemistry').removeClass('d-none');
        $('#span_chemistry').removeClass('d-none');
        $('div#div_id_modality_chemistry').removeClass('d-none');
        $('#span_modality_chemistry').removeClass('d-none');
    }
    else{
        $('#id_chemistry').val('');
        $('select#id_modality_chemistry').val("");
    }

    // attended_physics
    if(attended_physics == 'yes'){
        $('div#div_id_physics').removeClass('d-none');
        $('#span_physics').removeClass('d-none');
        $('div#div_id_modality_physics').removeClass('d-none');
        $('#span_modality_physics').removeClass('d-none');
    }
    else{
        $('#id_physics').val('');
        $('select#id_modality_physics').val("");
    }


    // pss_session_modality
    $('div#div_id_pss_session_number').addClass('d-none');
    $('#span_pss_session_number ').addClass('d-none');
    $('div#div_id_pss_session_modality ').addClass('d-none');
    $('#span_pss_session_modality ').addClass('d-none');
    if(pss_session_attended == 'yes'){
        $('div#div_id_pss_session_number').removeClass('d-none');
        $('#span_pss_session_number').removeClass('d-none');
        $('div#div_id_pss_session_modality').removeClass('d-none');
        $('#span_pss_session_modality').removeClass('d-none');
    }
    else{
        $('#id_pss_session_number').val('');
        $('select#div_id_pss_session_modality').val("");
    }

    // covid_session_attended
    $('div#div_id_covid_session_number').addClass('d-none');
    $('#span_covid_session_number ').addClass('d-none');
    $('div#div_id_covid_session_modality ').addClass('d-none');
    $('#span_covid_session_modality ').addClass('d-none');
    if(covid_session_attended == 'yes'){
        $('div#div_id_covid_session_number').removeClass('d-none');
        $('#span_covid_session_number').removeClass('d-none');
        $('div#div_id_covid_session_modality').removeClass('d-none');
        $('#span_covid_session_modality').removeClass('d-none');
    }
    else{
        $('#id_covid_session_number').val('');
        $('select#div_id_covid_session_modality').val("");
    }

    // followup_session_attended
    $('div#div_id_followup_session_number').addClass('d-none');
    $('#span_followup_session_number ').addClass('d-none');
    $('div#div_id_followup_session_modality ').addClass('d-none');
    $('#span_followup_session_modality ').addClass('d-none');
    if(followup_session_attended == 'yes'){
        $('div#div_id_followup_session_number').removeClass('d-none');
        $('#span_followup_session_number').removeClass('d-none');
        $('div#div_id_followup_session_modality').removeClass('d-none');
        $('#span_followup_session_modality').removeClass('d-none');
    }
    else{
        $('#id_followup_session_number').val('');
        $('select#div_id_followup_session_modality').val("");
    }

    // parent_attended
    $('#div_id_parent_attended_other').addClass('d-none');
    $('#span_parent_attended_other').addClass('d-none');
    if(parent_attended == 'other'){
    $('#div_id_parent_attended_other').removeClass('d-none');
    $('#span_parent_attended_other').removeClass('d-none');
    }
    else
    {
        $('#id_parent_attended_other').val('');
    }


}


function moved_student(item, moved_date)
{
    var data = {moved: item, moved_date: moved_date};

    $.ajax({
        type: "POST",
        url: '/api/logging-student-move/',
        data: data,
        cache: false,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            console.log(response);
        },
        error: function(response) {
            console.log(response);
        }
    });
}

function dropout_student_enrollment(dropout_status, dropout_date)
{
    var data = {dropout_status: dropout_status, dropout_date: dropout_date};

    $.ajax({
        type: "POST",
        url: '/api/student-dropout-enrollment/',
        data: data,
        cache: false,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            console.log(response);
        },
        error: function(response) {
            console.log(response);
        }
    });
}

function justify_student_enrollment(justify_status, justify_date)
{
    var data = {justify_status: justify_status, justify_date: justify_date};

    $.ajax({
        type: "POST",
        url: '/api/student-justify-enrollment/',
        data: data,
        cache: false,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            console.log(response);
        },
        error: function(response) {
            console.log(response);
        }
    });
}

function delete_student(item, callback)
{
    var url = item.attr('data-action');

    $.ajax({
        type: "DELETE",
        url: url+'/',
        cache: false,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            if(callback != undefined){
                callback();
            }
            console.log(response);
        },
        error: function(response) {
            console.log(response);
        }
    });
}

function patch_registration(item, callback)
{
    var url = item.attr('data-action');
    var data = {section: '', registered_in_level: ''};

    $.ajax({
        type: "PATCH",
        url: url+'/',
        cache: false,
        data: data,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            if(callback != undefined){
                callback();
            }
            console.log(response);
        },
        error: function(response) {
            console.log(response);
        }
    });
}

// log student move from ALP to 2nd shift
function log_student_program_move(item, eligibility)
{
    var data = {
        student: item.student_id,
        registry: item.id,
        school_from: item.school,
        school_to: current_school,
        eligibility: eligibility
    };

    $.ajax({
        type: "POST",
        url: '/api/logging-student-program-move/',
        data: data,
        cache: false,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            console.log(response);
        },
        error: function(response) {
            console.log(response);
        }
    });
}


function verify_age_level()
{
    var level = $('select#id_classroom').val();
    var day = $('select#id_student_birthday_day').val();
    var month = $('select#id_student_birthday_month').val();
    var year = $('select#id_student_birthday_year').val();
    var birthday = year+"-"+month+"-"+day;
    var dob = new Date(birthday);
    //var min_date = new Date('2019-01-31');
    var min_date = new Date('2020-01-31');

    if(dob == NaN || level == '') {
        return false;
    }

    if(level == '1') { //KG
        //min_date = new Date('2018-09-14');
        min_date = new Date('2019-09-14');
        display_alert_restriction(dob, 5, 9, min_date);
    }
    if(level == '2') { //Level 1
        display_alert_restriction(dob, 6, 10, min_date);
    }
    if(level == '3') { //Level 2
        display_alert(dob, 7, 13, min_date);
    }
    if(level == '4') { //Level 3
        display_alert(dob, 8, 14, min_date);
    }
    if(level == '5') { //Level 4
        display_alert(dob, 9, 15, min_date);
    }
    if(level == '6') { //Level 5
        display_alert(dob, 10, 18, min_date);
    }
    if(level == '7') { //Level 6
        display_alert(dob, 11, 18, min_date);
    }
    if(level == '8') { //Level 7
        display_alert(dob, 12, 18, min_date);
    }
    if(level == '9') { //Level 8
        display_alert(dob, 13, 19, min_date);
    }
    if(level == '10') { //Level 9
        display_alert(dob, 14, 20, min_date);
    }
}

function display_alert_restriction(dob, min_value, max_value, min_date)
{
    var today = new Date();
    var min_age = Math.floor((min_date-dob) / (365.25 * 24 * 60 * 60 * 1000));
    var max_age = Math.floor((today-dob) / (365.25 * 24 * 60 * 60 * 1000));

    if(min_age < min_value) {
        $('#id_age_min_restricted').val(1);
        var msg1 = min_age_restriction_msg;
        showModal(msg1);
        $('select#id_student_birthday_year').val("");
        return false;
    }
    if(max_age > max_value) {
        $('#id_age_max_restricted').val(1);
        var msg2 = max_age_limit_msg;
        if(confirm(msg2)){

        }else{
            $('select#id_student_birthday_year').val("");
        }
        return false;
    }
    return true;
}

function display_alert(dob, min_value, max_value, min_date)
{
    var today = new Date();
    var min_age = Math.floor((min_date-dob) / (365.25 * 24 * 60 * 60 * 1000));
    var max_age = Math.floor((today-dob) / (365.25 * 24 * 60 * 60 * 1000));

    if(min_age < min_value) {
        $('#id_age_min_restricted').val(1);
        var msg1 = min_age_limit_msg;
        if(confirm(msg1)){

        }else{
            $('select#id_student_birthday_year').val("");
        }
        return false;
    }
    if(max_age > max_value) {
        $('#id_age_max_restricted').val(1);
        var msg2 = max_age_limit_msg;
        if(confirm(msg2)){

        }else{
            $('select#id_student_birthday_year').val("");
        }
        return false;
    }
    return true;
}

function window_location(value)
{
    console.log('OK');
    $('head').append('<meta http-equiv="refresh" content="0; URL='+value+'" id="redirect"/>');
}

function load_districts(url)
{
    var value = $("#id_governorate").val();
    $.ajax({
        url: url,
        data: {
            'id_governorate': value
        },
        success: function (data) {
            $("#id_district").html(data);
        }
    })
}
function load_cadasters(url)
{
    var value = $("#id_district").val();
    $.ajax({
        url: url,
        data: {
            'id_district': value
        },
        success: function (data) {
            $("#id_cadaster").html(data);
        }
    })
}

