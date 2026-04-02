$(document).ready(function () {
    setupReferralForm();
    bindReferralEvents();
    reorganizeForm();
});

function setupReferralForm() {
    if ($('#id_dropout_date').length === 1) {
        const today = new Date().toISOString().split('T')[0];

        $('#id_dropout_date').attr('type', 'date');
        $('#id_dropout_date').attr('max', today);

        if ($.fn.datepicker) {
            $('#id_dropout_date').datepicker('destroy');
            $('#id_dropout_date').datepicker({
                dateFormat: "yy-mm-dd",
                maxDate: 0
            });
        }
    }
}

function bindReferralEvents() {
    $(document).off('change.referral');

    $(document).on('change.referral', '#id_referred_service', function () {
        reorganizeForm();
    });

    $(document).on('change.referral', '#id_referred_formal_education', function () {
        reorganizeForm();
    });

    $(document).on('change.referral', '#id_recommended_learning_path', function () {
        reorganizeForm();
    });

    $(document).off('submit.referral', 'form');
    $(document).on('submit.referral', 'form', function (e) {
        reorganizeForm();

        const referredService = ($('#id_referred_service').val() || '').trim();
        const recommendedLearningPath = ($('#id_recommended_learning_path').val() || '').trim();
        const referredFormalEducation = ($('#id_referred_formal_education').val() || '').trim();
        const dropoutDate = ($('#id_dropout_date').val() || '').trim();
        const today = new Date().toISOString().split('T')[0];

        $('#id_referred_service_other').prop('required', referredService === 'Other');
        $('#id_dropout_date').prop('required', recommendedLearningPath === 'Drop out');
        $('#id_referred_school').prop('required', referredFormalEducation === 'Yes');

        if (recommendedLearningPath === 'Drop out' && dropoutDate && dropoutDate > today) {
            alert('Dropout date cannot be in the future.');
            $('#id_dropout_date').focus();
            e.preventDefault();
            return false;
        }

        return true;
    });
}

function reorganizeForm() {
    const referredService = ($('#id_referred_service').val() || '').trim();
    const referredFormalEducation = ($('#id_referred_formal_education').val() || '').trim();
    const recommendedLearningPath = ($('#id_recommended_learning_path').val() || '').trim();

    const $referredServiceOtherWrapper = $('#referred-service-other-wrapper');
    const $dropoutDateWrapper = $('#dropout-date-wrapper');
    const $referredSchoolWrapper = $('#referred-school-wrapper');

    const $referredServiceOther = $('#id_referred_service_other');
    const $dropoutDate = $('#id_dropout_date');
    const $referredSchool = $('#id_referred_school');

    // referred service other
    if (referredService === 'Other') {
        $referredServiceOtherWrapper.removeClass('d-none').show();
    } else {
        $referredServiceOtherWrapper.addClass('d-none').hide();
        $referredServiceOther.val('').removeClass('error-field');
        $referredServiceOther.prop('required', false);
    }

    // referred school
    if ($('#id_referred_formal_education').length && referredFormalEducation === 'Yes') {
        $referredSchoolWrapper.removeClass('d-none').show();
    } else {
        $referredSchoolWrapper.addClass('d-none').hide();
        $referredSchool.removeClass('error-field');
        $referredSchool.prop('required', false);
        try {
            $referredSchool.val(null).trigger('change');
        } catch (e) {
            $referredSchool.val('');
        }
    }

    // dropout date
    if (recommendedLearningPath === 'Drop out') {
        $dropoutDateWrapper.removeClass('d-none').show();
    } else {
        $dropoutDateWrapper.addClass('d-none').hide();
        $dropoutDate.val('').removeClass('error-field');
        $dropoutDate.prop('required', false);
    }
}