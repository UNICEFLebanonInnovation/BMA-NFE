function translateMessage(message) {
    return window.gettext ? window.gettext(message) : message;
}

var protocol = window.location.protocol;
var host = protocol+window.location.host;

$(document).ready(function() {

    $(document).on('click', '#save_attendance_teachers', function(e){
        e.preventDefault();

        let isValid = true;
        $('.is-invalid').removeClass('is-invalid'); // reset styles

        var attendance_date = $("#attendance_date").val();
        teachers_attendance = [];

        $(".list-group-item").each(function () {
            var $item = $(this);
            var teacher_id = $item.find(".teacher_id").val();
            var status = $item.find("input.status:checked").val() || "Present";

            teachers_attendance.push({
                "teacher_id": teacher_id,
                "status": status,
            });
        });

        if (!isValid) {
            $('#formErrorModal').modal('show');
            return;
        }

        $('.app-drawer-overlay').removeClass('d-none');
        $('#save_attendance_teachers').addClass('disabled');

        var attendance_information = {
           "attendance_date": attendance_date,
           "teachers_attendance": teachers_attendance
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
                $('#save_attendance_teachers').removeClass('disabled');
                $('.app-drawer-overlay').addClass('d-none');
            }
        });
    });

    $(document).on('click', '#load_attendance_teachers', function(e){
        e.preventDefault();

        var attendance_date = $('#attendance_date').val();

        if (!attendance_date) {
             showModal(translateMessage('Please fill: Attendance Date.'));
             return false;
        }

        $('#attendance_teachers').empty().append("Loading...");

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            async: true,
            data: {
                'attendance_date': $("#attendance_date").val(),
                'school_id': $('#school_id').val(),
            },
            dataType: 'html',
            success: function (response) {
                $('#attendance_teachers').empty().append(response);

                var teachersCount = $('#attendance_teachers .teacher_id').length;
                $('#teachers_count').text(teachersCount);

                $('#save_attendance_teachers').removeClass('disabled');
                $('.app-drawer-overlay').addClass('d-none');
            },
            error: function(response) {
                console.log(response);
                $('.app-drawer-overlay').addClass('d-none');
            }
        });
    });

    $('#attendance_date').on('change', function(e) {
        $('#attendance_teachers').empty("");
        $('#teachers_count').text(0);
        $('#save_attendance_teachers').addClass('disabled');
        $('#load_attendance_teachers').removeClass('disabled');
    });
});
