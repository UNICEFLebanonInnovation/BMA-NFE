function translateMessage(message) {
    return window.gettext ? window.gettext(message) : message;
}


var protocol = window.location.protocol;
var host = protocol+window.location.host;

function csvCell(value) {
    var text = String(value == null ? '' : value);

    // Prevent spreadsheet applications from interpreting user-entered text
    // as a formula when the CSV is opened.
    if (/^[=+\-@]/.test(text)) {
        text = "'" + text;
    }

    return '"' + text.replace(/"/g, '""') + '"';
}

function downloadAttendanceCsv() {
    var rows = [[
        'Child', 'Mother', 'Date of birth', 'Nationality',
        'Attendance date', 'Programme', 'Round', 'Status', 'Absence reason', 'Other details'
    ]];

    $('#attendance_children .list-group-item').each(function () {
        var $item = $(this);
        var status = $item.find('input.status:checked').val() || '';

        rows.push([
            $item.data('child-name'),
            $item.data('mother-name'),
            $item.data('birthday'),
            $item.data('nationality'),
            $('#attendance_date').val(),
            $('#programme option:selected').text().trim(),
            $('#round option:selected').text().trim(),
            status === 'Yes' ? 'Attended' : 'Absent',
            status === 'No' ? $item.find('.absence_reason').val() : '',
            status === 'No' ? $item.find('.absence_reason_other').val() : ''
        ]);
    });

    if (rows.length === 1) {
        showModal(translateMessage('Load attendance before downloading.'));
        return;
    }

    var csv = '\uFEFF' + rows.map(function (row) {
        return row.map(csvCell).join(',');
    }).join('\r\n');
    var url = URL.createObjectURL(new Blob([csv], {type: 'text/csv;charset=utf-8'}));
    var link = document.createElement('a');
    link.href = url;
    link.download = 'alp_attendance_' + $('#attendance_date').val() + '.csv';
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}

$(document).ready(function() {

    $(document).on('click', '#download_attendance', downloadAttendanceCsv);

    $('.attendance_day_off input').on('change', function() {
        var attendance_day_off = $(this).val();

        if (attendance_day_off == 'Yes') {
            $('#close_reason').removeClass('hidden');
            $('#load_attendance_children').addClass('disabled');
            $('#save_attendance_children').removeClass('disabled');
            $('#download_attendance').addClass('disabled').prop('disabled', true);
            $('#attendance_children').empty("");
        } else {
            $('#close_reason').addClass('hidden');
            $('#load_attendance_children').removeClass('disabled');
        }
    });

    $(document).on('click', '#save_attendance_children', function(e){
    e.preventDefault();

    let isValid = true;
    $('.is-invalid').removeClass('is-invalid'); // reset styles

    var attendance_day_off = $("input[name='attendance_day_off']:checked").val();
    var attendance_date = $("#attendance_date").val();
    var programme = $("#programme").val();

    var close_reason = $("#close_reason").val();
    var round_id = $("#round").val();
    children_attendance = [];

    $(".list-group-item").each(function () {
        var $item = $(this);
        var child_id = $item.find(".child_id").val();
        var registration_id = $item.find(".registration_id").val();
        var attended = $item.find("input.status:checked").val() || "Yes";
        var absence_reason = $item.find(".absence_reason").val();
        var absence_reason_other = $item.find(".absence_reason_other").val();

        // Validation logic
        if (attended === 'No') {
            if (!absence_reason) {
                $item.find(".absence_reason").addClass("is-invalid");
                isValid = false;
            } else if (absence_reason === 'Other' && !absence_reason_other.trim()) {
                $item.find(".absence_reason_other").addClass("is-invalid");
                isValid = false;
            }
        }

        children_attendance.push({
            "child_id": child_id,
            "registration_id": registration_id,
            "attended": attended,
            "absence_reason": absence_reason,
            "absence_reason_other": absence_reason_other
        });
    });

    if (!isValid) {
        $('#formErrorModal').modal('show');
        return;
    }

    $('.app-drawer-overlay').removeClass('d-none');
    $('#save_attendance_children').addClass('disabled');

    var attendance_information = {
       "attendance_date": attendance_date,
       "attendance_day_off": attendance_day_off,
       "close_reason": close_reason,
       "programme": programme,

       "round_id": round_id,
       "children_attendance": children_attendance
    };

    $.ajax({
        type: "POST",
        url: $(this).attr('href'),
        cache: false,
        headers: getHeader(),
        data: JSON.stringify(attendance_information),
        async: true,
        dataType: 'json',
        success: function (response) {
            if (response.result) {
                $('.app-drawer-overlay').addClass('d-none');
                $('#formSuccessModal').modal('show');
            }
            console.log(response);
        },
        error: function(response) {
            console.log(response);
            $('.app-drawer-overlay').addClass('d-none');
        },
        complete: function() {
            $('#save_attendance_children').removeClass('disabled');
            $('.app-drawer-overlay').addClass('d-none');
        }
    });
});

    $(document).on('click', '#load_attendance_children', function(e){
        e.preventDefault();

        var programme = $('#programme').val();
        var round_id = $('#round').val();


        if (!programme || !round_id) {
             showModal(translateMessage('Please fill: Attendance Date, Round, and Programme.'));
             return false;
        }

        $('#attendance_children').empty().append("Loading...");

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            async: true,
            data: {
                'attendance_date': $("#attendance_date").val(),
                'school_id': $('#school_id').val(),
                'round_id': round_id,
                'programme': programme,

            },
            dataType: 'html',
            success: function (response) {
                $('#attendance_children').empty().append(response);

                var childrenCount = $('#attendance_children .registration_id').length;
                $('#children_count').text(childrenCount);

                $('#save_attendance_children').removeClass('disabled');
                $('#download_attendance')
                    .toggleClass('disabled', childrenCount === 0)
                    .prop('disabled', childrenCount === 0);
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

    $('#attendance_date').on('change', function(e) {
        $('#attendance_children').empty("");
        $('#children_count').text(0);
        $('#save_attendance_children').addClass('disabled');
        $('#download_attendance').addClass('disabled').prop('disabled', true);
        $('#load_attendance_children').removeClass('disabled');
    });


        function resetAttendanceUI() {
            $('#attendance_children').empty("");
            $('#children_count').text(0);
            $('#save_attendance_children').addClass('disabled');
            $('#download_attendance').addClass('disabled').prop('disabled', true);
            $('#load_attendance_children').removeClass('disabled');
        }

        // Trigger on all critical field changes
        $('#round, #programme').on('change', function() {
            resetAttendanceUI();
        });

});
