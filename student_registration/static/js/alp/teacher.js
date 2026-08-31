(function ($) {
    'use strict';

    function toggleConditionalFields() {
        var hasExtraCoaching = $('#id_extra_coaching').val() === 'yes';
        var teacherAssignment = $('#id_teacher_assignment').val();
        var hasPrivateAssignment = teacherAssignment === 'ALP and private';
        var hasOtherAssignment = teacherAssignment === 'other';

        $('#div_id_extra_coaching_specify').toggleClass('d-none', !hasExtraCoaching);
        $('#id_extra_coaching_specify').prop('required', hasExtraCoaching);

        $('#div_id_teacher_assignment_other').toggleClass('d-none', !hasOtherAssignment);
        $('#id_teacher_assignment_other').prop('required', hasOtherAssignment);
        if (!hasOtherAssignment) {
            $('#id_teacher_assignment_other').val('');
        }

        $('#div_id_teaching_hours_private_school, #div_id_teaching_hours_mscc')
            .toggleClass('d-none', !hasPrivateAssignment);
        $('#id_teaching_hours_private_school, #id_teaching_hours_mscc')
            .prop('required', hasPrivateAssignment);
    }

    $(function () {
        toggleConditionalFields();
        $('#id_extra_coaching, #id_teacher_assignment').on('change', toggleConditionalFields);
    });
}(jQuery));
