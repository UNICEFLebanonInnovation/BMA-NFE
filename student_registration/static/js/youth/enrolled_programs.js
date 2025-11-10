

$(document).ready(function() {
    reorganizeForm();

    var initialGov = $('#id_governorate').val();
    var initialDistrict = $('#id_district').val();
    var initialCadaster = $('#id_cadaster').val();

    function toggleLocation() {
        var same = $('#id_same_location').is(':checked');
        if (same) {
            $('#id_governorate').val(initialGov).prop('disabled', true);
            $('#id_district').val(initialDistrict).prop('disabled', true);
            $('#id_cadaster').val(initialCadaster).prop('disabled', true);
        } else {
            $('#id_governorate').prop('disabled', false);
            $('#id_district').prop('disabled', false);
            $('#id_cadaster').prop('disabled', false);
        }
    }

    if($('#id_same_location').length === 1) {
        toggleLocation();
        $('#id_same_location').on('change', toggleLocation);
    }

    if($(document).find('#id_dropout_date').length == 1) {
        $('#id_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_registration_date').length == 1) {
        $('#id_registration_date').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_completion_date').length == 1) {
        $('#id_completion_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', 'select#id_education_status', function(){
        reorganizeForm();
    });

    $('form').on('submit', function(){
        $('#id_governorate,#id_district,#id_cadaster').prop('disabled', false);
    });
});

function reorganizeForm()
{
    //    Education Status
   var education_status = $('select#id_education_status').val();

    $('div#div_id_dropout_date').addClass('d-none');
    $('#span_dropout_date').addClass('d-none');

    if(education_status == 'Currently registered in Formal Education school but not attending'){
        $('#div_id_dropout_date').removeClass('d-none');
        $('#span_dropout_date').removeClass('d-none');
        $('#id_dropout_date').addClass('error-field');
    }
    else
    {
        $('div#div_id_dropout_date').addClass('d-none');
        $('#id_dropout_date').removeClass('error-field');
        $('#id_dropout_date').val('');
    }
}



function load_program_document(url)
{
    var value = $("#id_donor").val();
    $.ajax({
        url: url,
        data: {
            'id_donor': value
        },
        success: function (data) {
            $("#id_program_document").html(data);
        }
    })
}

function load_master_program(url)
{
    var value = $("#id_program_document").val();
    $.ajax({
        url: url,
        data: {
            'id_program_document': value
        },
        success: function (data) {
            $("#id_master_program").html(data);
        }
    })
}

function load_sub_programs(url)
{
    var value = $("#id_master_program").val();
    $.ajax({
        url: url,
        data: {
            'id_master_program': value
        },
        success: function (data) {
            $("#id_sub_program").html(data);
        }
    })
}

function load_districts(url)
{
    var value = $("#id_governorate").val();
    $.ajax({
        url: url,
        data: {
            'id_adolescent_governorate': value
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
            'id_adolescent_district': value
        },
        success: function (data) {
            $("#id_cadaster").html(data);
        }
    })
}

function urlParam(name){
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	if (results && results.length){
        return results[1] || 0;
    }
    return 0;
}
