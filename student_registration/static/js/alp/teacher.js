(function ($) {
    'use strict';

    function toggleConditionalFields() {
        var hasExtraCoaching = $('#id_extra_coaching').val() === 'yes';
        var hasPrivateAssignment = $('#id_teacher_assignment').val() === 'Private and Makani';

        $('#div_id_extra_coaching_specify').toggleClass('d-none', !hasExtraCoaching);
        $('#id_extra_coaching_specify').prop('required', hasExtraCoaching);

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
