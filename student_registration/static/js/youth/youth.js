
var english_fields = "#id_adolescent_first_name, #id_adolescent_father_name, #id_adolescent_last_name, #id_adolescent_mother_fullname, " +
    " #id_caregiver_mother_name, #id_caregiver_last_name, #id_caregiver_middle_name, #id_caregiver_first_name";

$(document).ready(function() {


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

    $(document).on('change', 'select#id_adolescent_gender', function(){
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

    $(document).on('change', 'select#id_adolescent_have_children, select#id_adolescent_nationality, select#id_main_caregiver, select#id_main_caregiver_nationality, select#id_have_labour, select#id_labour_type, select#id_adolescent_have_sibling', function(){
         reorganizeForm();
    });
    $(document).on('change', 'select#id_student_nationality, select#id_have_labour_single_selection, select#id_labour_weekly_income', function(){
        reorganizeForm();
    });

    $(document).on('change', '#id_adolescent_first_name, #id_adolescent_father_name, #id_adolescent_last_name, #id_adolescent_mother_fullname, #id_adolescent_gender, #id_adolescent_birthday_year, #id_adolescent_birthday_month, #id_adolescent_birthday_day, #id_adolescent_nationality', function(){
        $('#search_loader').removeClass('hidden');
        $('#nfe_search_loader').removeClass('hidden');

//        var first_name = $('#id_adolescent_first_name').val();
//        var father_name = $('#id_adolescent_father_name').val();
//        var last_name = $('#id_adolescent_last_name').val();
//        if ( first_name!= '' && father_name!= '' && last_name!= '')
//        {
//            outreach_adolescent_search();
//        }
        adolescent_duplication_check();
    });

    $(document).on('change', 'select#id_main_caregiver', function(){
        var main_caregiver = $('select#id_main_caregiver').val();
        if(main_caregiver == 'Father'){
            var father_name = $('#id_adolescent_father_name').val();
            var last_name = $('#id_adolescent_last_name').val();
            $('#id_caregiver_first_name').val(father_name);
            $('#id_caregiver_last_name').val(last_name);
        }
        else {
            $('#id_caregiver_first_name').val('');
            $('#id_caregiver_last_name').val('');
        }
    });

    $(document).on('blur', english_fields, function(){
        checkEnglishOnly($(this));
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
        if(typeof validateMainForm === 'function' && !validateMainForm(false)){
            error_fields = true;
        }
        if(!error_fields){
            $('#next-btn22').trigger('click');
            $(this).removeClass('error-field');
         }else{
            $('#formErrorModal').modal('show');
         }
    });


});


function append_new_result(data)
{

    var child_html = '';
    $('#outreach_search_result').empty();
    $('#search_loader').addClass('hidden');

    $(data.result).each(function(i, item) {
        var full_name = "";
        full_name = full_name.concat(item.first_name, " ", item.outreach_caregiver__father_name, " ", item.outreach_caregiver__last_name);

        var html_line1 = '<div class="vertical-timeline-item vertical-timeline-element"><div><div class="vertical-timeline-element-icon bounce-in"><div class="timeline-icon border-success"><span class="text-success">'+ item.score +'%</span></div></div><div class="vertical-timeline-element-content bounce-in">';
        var html_line2 = '<h4 class="timeline-title text-success"><a href="javascript:get_child_data('+ item.id +');">'+full_name+'</a></h4>';
        var html_line3 = '<p>'+ item.date_of_birth + ' - '+ item.outreach_caregiver__mother_full_name +'</p>';
        var html_line4 = '<p>'+ item.gender + ' - '+ item.nationality +'</p></div></div></div>';

        child_html = html_line1 + html_line2 + html_line3 + html_line4;

        $('#outreach_search_result').append(child_html);
    });

    if(data.result.length == 0) {
        var html_line1 = '<div class="vertical-timeline-item vertical-timeline-element"><div><div class="vertical-timeline-element-icon bounce-in"><div class="timeline-icon border-danger"><i class="lnr-cross text-danger"></i></div></div><div class="vertical-timeline-element-content bounce-in">';
        var html_line2 = '<h4 class="timeline-title text-danger">No result found</h4>';
        var html_line3 = '<p></p>';
        var html_line4 = '<p></p></div></div></div>';

        child_html = html_line1 + html_line2 + html_line3 + html_line4;

        $('#outreach_search_result').append(child_html);

    }
}

function get_child_data(outreach_id)
{
    $('#search_loader').removeClass('hidden');

    $.ajax({
        url: '/MSCC/Outreach-Child/',
        data: { outreach_id: outreach_id},
        cache: false,
        async: true,
        dataType: 'json',
        success: function (response) {
            fill_outreach_child_data(response);
        },
        error: function (response) {
            console.log(response);
        }
    });
}

function fill_outreach_child_data(data)
{
    $('#search_loader').addClass('hidden');
    $(data).each(function(i, item) {
        console.log(item);
        {
            Object.keys(item).forEach(key => {
                $('#id_'+ key).val(item[key]);
            });
        }
    });
    $('#search_loader').addClass('hidden');
}

function load_districts(url)
{
    var value = $("#id_adolescent_governorate").val();
    $.ajax({
        url: url,
        data: {
            'id_adolescent_governorate': value
        },
        success: function (data) {
            $("#id_adolescent_district").html(data);
        }
    })
}

function load_cadasters(url)
{
    var value = $("#id_adolescent_district").val();
    $.ajax({
        url: url,
        data: {
            'id_adolescent_district': value
        },
        success: function (data) {
            $("#id_adolescent_cadaster").html(data);
        }
    })
}

function old_child_search() {

    if (isAddPage()) {

        var birthday_year = $('#id_adolescent_birthday_year').val();
        var birthday_month = $('#id_adolescent_birthday_month').val();
        var birthday_day = $('#id_adolescent_birthday_day').val();
        var first_name = $('#id_adolescent_first_name').val();
        var father_name = $('#id_adolescent_father_name').val();
        var last_name = $('#id_adolescent_last_name').val();

        var data = {
            birthday_year: birthday_year,
            birthday_month: birthday_month,
            birthday_day: birthday_day,
            first_name: first_name,
            father_name: father_name,
            last_name: last_name,
        };

        $.ajax({
            url: '/MSCC/Old-Child-Search/',
            dataType: "json",
            data: data,
            cache: false,
            async: true,
            success: function (response) {
                append_old_result(response);
            },
            error: function (response) {
                console.log(response);
            }
        });
    }
}

function adolescent_duplication_check() {

    $('#child-duplication-error').hide();
    $('#submit-id-save').prop('disabled', false);

    var birthday_year = $('#id_adolescent_birthday_year').val();
    var birthday_month = $('#id_adolescent_birthday_month').val();
    var birthday_day = $('#id_adolescent_birthday_day').val();
    var first_name = $('#id_adolescent_first_name').val();
    var father_name = $('#id_adolescent_father_name').val();
    var last_name = $('#id_adolescent_last_name').val();
    var mother_fullname = $('#id_adolescent_mother_fullname').val();
    var sex = $('#id_adolescent_gender').val();
    var nationality = $('#id_adolescent_nationality').val();

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
            url: '/youth/Child-Duplication-Check/',
            data: JSON.stringify(data),
            cache: false,
            async: true,
            headers: requestHeaders,
            dataType: 'json',
            success: function (response) {
                if (response.has_duplicate) {
                    const partnerName = response.partner_name || 'another partner';
                    $('#child-duplication-error-text')
                      .html(`Another adolescent already has this UNICEF ID with partner <b>${partnerName}</b>.`);
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
        url: '/MSCC/Get-Old-Child-Data/',
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


function isAddPage()
{
    if( $(document).find('#outreach-nfe-result').length == 1) {
        return true;
    }
    return false;
}


function reorganizeForm()
{
//  adolescent_gender
    var adolescent_gender = $('select#id_adolescent_gender').val();

    if(adolescent_gender =='Female'){
        $("#id_adolescent_have_children").append('<option value="Child pregnant or expecting children">Child pregnant or expecting children</option>');
    }
    else
     {
        $("#id_adolescent_have_children option[value='Child pregnant or expecting children']").remove();
    }

//    Child Nationality
    var child_nationality = $('select#id_adolescent_nationality').val();
    $('div#div_id_adolescent_nationality_other').addClass('d-none');

    if(child_nationality == 6){
        $('#div_id_adolescent_nationality_other').removeClass('d-none');
    }
    else{
        $('#id_adolescent_nationality_other').val('');
    }


//   Source of Identification
    var source_of_identification = $('select#id_source_of_identification').val();
    $('div#div_id_source_of_identification_specify').addClass('d-none');
    $('#span_source_of_identification_specify').addClass('d-none');

    if(source_of_identification == 'Other Sources'){
        $('#div_id_source_of_identification_specify').removeClass('d-none');
        $('#span_source_of_identification_specify').removeClass('d-none');
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
    if(id_type == 12){
        $('div.child_id8').removeClass('d-none');
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
