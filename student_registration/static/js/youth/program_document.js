
$(document).ready(function() {
    if($(document).find('#id_start_date').length == 1) {
        $('#id_start_date').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_end_date').length == 1) {
        $('#id_end_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    // Select the population groups checkboxes and the target number fields
    const populationGroups = $('input[name="population_groups"]');
    const numberTargetedSyrians = $('#id_number_targeted_syrians');
    const numberTargetedLebanese = $('#id_number_targeted_lebanese');
    const numberTargetedPrl = $('#id_number_targeted_prl');
    const numberTargetedPrs = $('#id_number_targeted_prs');

    function updateTargetedFields() {
        // Get selected labels
        const selectedLabels = populationGroups.filter(':checked').map(function() {
//            return $(this).val();
            return $(this).closest('label').text().trim();
        }).get();

        // Logic to enable/disable based on selected groups
        console.log(selectedLabels)
        if (!selectedLabels.includes('Syrians')) {
            numberTargetedSyrians.prop('disabled', true).val('');
        } else {
            numberTargetedSyrians.prop('disabled', false);
        }
        if (!selectedLabels.includes('Lebanese')) {
            numberTargetedLebanese.prop('disabled', true).val('');
        } else {
            numberTargetedLebanese.prop('disabled', false);
        }
        if (!selectedLabels.includes('PRL')) {
            numberTargetedPrl.prop('disabled', true).val('');
        } else {
            numberTargetedPrl.prop('disabled', false);
        }

        if (!selectedLabels.includes('PRS')) {
            numberTargetedPrs.prop('disabled', true).val('');
        } else {
            numberTargetedPrs.prop('disabled', false);
        }
    }

    // Add event listeners to checkboxes
    populationGroups.on('change', updateTargetedFields);

    // Initial call to set the state correctly on page load
    updateTargetedFields();

});

