
$(document).ready(function() {

    // Initialize Bootstrap 5 Modals
    const deleteModal = document.getElementById('deleteConfirmModal') ? new bootstrap.Modal(document.getElementById('deleteConfirmModal')) : null;
    const exportModal = document.getElementById('exportOptionsModal') ? new bootstrap.Modal(document.getElementById('exportOptionsModal')) : null;
    const registrationModal = document.getElementById('child-registration-modal') ? new bootstrap.Modal(document.getElementById('child-registration-modal')) : null;

    // Handle Delete Student
    $(document).on("click", ".delete-student", function(e) {
        e.preventDefault();
        var registrationId = $(this).data("registration-id");
        var parentTR = $(this).closest('tr');
        var modalEl = document.getElementById('deleteConfirmModal');
        $(modalEl).data('registrationId', registrationId);
        $(modalEl).data('parentTR', parentTR);
        if (deleteModal) deleteModal.show();
    });

    $(document).on('click', '#deleteConfirmModal .confirm-delete', function() {
        var modalEl = document.getElementById('deleteConfirmModal');
        var registrationId = $(modalEl).data('registrationId');
        var parentTR = $(modalEl).data('parentTR');
        var requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        $.ajax({
            url: "/mscc/child-mark-delete/" + registrationId + "/",
            type: "GET",
            headers: requestHeaders,
            success: function(data) {
                parentTR.fadeOut(300, function() { $(this).remove(); });
            },
            complete: function() {
                if (deleteModal) deleteModal.hide();
            }
        });
    });

    // Handle Export
    $(document).on('click', '.download-report-async', function(e) {
        e.preventDefault();
        if (exportModal) exportModal.show();
    });

    $(document).on('click', '#exportOptionsModal .start-export', function() {
        var params = $('#filter-form').serialize();
        var round = $("#id_round").val();
        var button = $(this);
        var originalHtml = button.html();

        if (!round) {
            if (exportModal) exportModal.hide();
            showModal('Please select a Round in the Advanced Search filters before exporting data.');
            return;
        }

        button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span> Exporting...');

        $.ajax({
            url: "/mscc/export-list-background/?" + params,
            type: 'GET',
            headers: getHeader(),
            success: function() {
                if (exportModal) exportModal.hide();
                showModal('Export started. You will be notified when the file is ready for download.');
            },
            error: function() {
                showModal('Failed to start export. Please try again later.');
            },
            complete: function() {
                button.prop('disabled', false).html(originalHtml);
            }
        });
    });

    // Active Filters Display Logic
    function updateActiveFilters() {
        const $container = $('#active-filters');
        $container.empty();

        $('#filter-form').find('select, input').each(function() {
            const $field = $(this);
            const val = $field.val();
            if (val && val !== '' && $field.attr('type') !== 'hidden' && $field.attr('name') !== 'csrfmiddlewaretoken') {
                let label = '';
                if ($field.is('select')) {
                    label = $field.find('option:selected').text();
                } else {
                    label = val;
                }

                const fieldLabel = $("label[for='" + $field.attr('id') + "']").text() || $field.attr('placeholder') || $field.attr('name');

                const $chip = $('<div class="badge bg-light text-dark border p-2 d-flex align-items-center">' +
                                '<span class="fw-bold me-1">' + fieldLabel + ':</span> ' + label +
                                '<button type="button" class="btn-close ms-2" style="font-size: 0.5rem;" data-field="' + $field.attr('id') + '"></button>' +
                                '</div>');
                $container.append($chip);
            }
        });
    }

    $(document).on('click', '#active-filters .btn-close', function() {
        const fieldId = $(this).data('field');
        $('#' + fieldId).val('').trigger('change');
        $('#filter-form').submit();
    });

    updateActiveFilters();
});
