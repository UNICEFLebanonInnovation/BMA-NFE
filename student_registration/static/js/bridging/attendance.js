function translateMessage(message) {
    return window.gettext ? window.gettext(message) : message;
}

var protocol = window.location.protocol;
var host = protocol + window.location.host;

$(document).ready(function() {

    $('.attendance_day_off label').click(function(e) {
        setTimeout(function() {
            var attendance_day_off = $('input[name=attendance_day_off]:checked').val();

            if (attendance_day_off == 'Yes') {
                $('#close_reason').removeClass('hidden');
                $('#load_attendance_children').addClass('disabled');
                $('#save_attendance_children').removeClass('disabled');
                $('#attendance_children').empty("");
            } else {
                $('#close_reason').addClass('hidden');
                $('#load_attendance_children').removeClass('disabled');
            }
        }, 500);
    });

$(document).on('click', '#save_attendance_children', function(e){
    e.preventDefault();

    var attendance_date = $("#attendance_date").val();
    var attendance_day_off = $("input[name='attendance_day_off']:checked").val();
    var close_reason = $("#close_reason").val();
    var round_id = $("#round").val();
    var school_id = $("#school").val();
    var registration_level = $("#registration_level").val();

    if (!attendance_date || !attendance_day_off || !round_id || !school_id || !registration_level) {
        showModal(translateMessage('Please fill all mandatory fields: Attendance Date, Attendance Day Off, Round, School, and Registration Level.'));
        return false;
    }

    if (attendance_day_off == 'Yes' && !close_reason) {
        showModal(translateMessage('Close reason is mandatory.'));
        return false;
    }

    var children_attendance = [];
    var isValid = true;

    $(".list-group-item").each(function () {
        var $item = $(this);
        var child_id = $item.find(".child_id").val();
        var registration_id = $item.find(".registration_id").val();
        var attended = $item.find("input.status:checked").val() || "Yes";
        var absence_reason = $item.find(".absence_reason").val();
        var absence_reason_other = $item.find(".absence_reason_other").val();

        // Reset previous errors
        $item.find(".absence_reason").removeClass("is-invalid");
        $item.find(".absence_reason_other").removeClass("is-invalid");

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
    if (attendance_day_off === 'No' && children_attendance.length === 0) {
        showError(translateMessage('Cannot save attendance: no children attendance was provided.'));
        return false;
    }

    $('.app-drawer-overlay').removeClass('d-none');

    var attendance_information = {
        "attendance_date": attendance_date,
        "attendance_day_off": attendance_day_off,
        "close_reason": close_reason,
        "round_id": round_id,
        "school_id": school_id,
        "registration_level": registration_level,
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
        success: function(response) {
            if (response.result) {
                $('#formSuccessModal').modal('show');
            }
            $('.app-drawer-overlay').addClass('d-none');
        },
        error: function(response) {
            console.log(response);
            $('.app-drawer-overlay').addClass('d-none');
        }
    });
});

$(document).on('click', '#load_attendance_children', function(e) {
    e.preventDefault();

    var attendance_date = $("#attendance_date").val();
    var attendance_day_off = $("input[name='attendance_day_off']:checked").val();
    var round_id = $("#round").val();
    var school_id = $("#school").val();
    var registration_level = $("#registration_level").val();

    if (!attendance_date || !round_id || !school_id || !registration_level) {
        showModal(translateMessage('Please fill: Attendance Date, Round, School, and Registration Level.'));
        return false;
    }

    $('#attendance_children').empty("");
    $('#attendance_children').append("Loading...");
    $('.app-drawer-overlay').removeClass('d-none');

    $.ajax({
        type: "GET",
        url: $(this).attr('href'),
        cache: false,
        async: true,
        data: {
            'attendance_date': attendance_date,
            'round_id': round_id,
            'school_id': school_id,
            'registration_level': registration_level
        },
        dataType: 'html',
        success: function(response) {
            $('#attendance_children').empty("");
            $('#attendance_children').append(response);

            // Count and display number of children loaded
            var childrenCount = $(".list-group-item").length;
            $('#children_count').text(childrenCount);

            $('#save_attendance_children').removeClass('disabled');
            $('.app-drawer-overlay').addClass('d-none');
        },
        error: function(response) {
            console.log(response);
            $('.app-drawer-overlay').addClass('d-none');
        }
    });
});

    $('#attendance_date').click(function(e) {
        setTimeout(function() {
            $('#attendance_children').empty("");
            $('#children_count').text(0);
            $('#save_attendance_children').addClass('disabled');
            $('#load_attendance_children').removeClass('disabled');
        }, 500);
    });

    function resetAttendanceUI() {
        $('#attendance_children').empty("");
        $('#children_count').text(0);
        $('#save_attendance_children').addClass('disabled');
        $('#load_attendance_children').removeClass('disabled');
    }

    // Trigger on all critical field changes
    $('#round, #school, #registration_level').on('change', function() {
        resetAttendanceUI();
    });
});
