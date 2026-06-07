
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

    // Handle Export Popup Initiation
    $(document).on('click', '.download-report-async', function(e) {
        e.preventDefault();
        if (exportModal) exportModal.show();
    });


    function pollExportStatus(exportId, attemptsRemaining) {
        if (!exportId) {
            showModal(window.gettext ? window.gettext('Export started successfully. Please check the recent exports menu for the download link.') : 'Export started successfully. Please check the recent exports menu for the download link.');
            return;
        }

        $.ajax({
            url: "/mscc/export-status/" + exportId + "/",
            type: "GET",
            headers: getHeader(),
            success: function(data) {
                if (data.status === "done" && data.file_url) {
                    window.location.href = data.file_url;
                    showModal(window.gettext ? window.gettext('Export successful. Your download should start automatically. If it does not, please use the recent exports menu.') : 'Export successful. Your download should start automatically. If it does not, please use the recent exports menu.');
                    return;
                }

                if (data.status === "failed") {
                    showModal(window.gettext ? window.gettext('Export failed. Please try again later or contact support.') : 'Export failed. Please try again later or contact support.');
                    return;
                }

                if (attemptsRemaining > 0) {
                    setTimeout(function() {
                        pollExportStatus(exportId, attemptsRemaining - 1);
                    }, 2000);
                    return;
                }

                showModal(window.gettext ? window.gettext('Export is still processing. Please check the recent exports menu for the download link.') : 'Export is still processing. Please check the recent exports menu for the download link.');
            },
            error: function() {
                showModal(window.gettext ? window.gettext('Export started, but the download status could not be checked. Please check the recent exports menu.') : 'Export started, but the download status could not be checked. Please check the recent exports menu.');
            }
        });
    }

    // Common Export Handler Function
    function initiateExport(button, url, checkRound = false) {
        // Build export params from the filter form, but always read `round` from
        // the URL so exports match the currently applied round filter.
        var paramsObj = new URLSearchParams($('#filter-form').serialize() || '');
        var roundFromUrl = new URLSearchParams(window.location.search || '').get('round');
        if (roundFromUrl !== null) {
            paramsObj.set('round', roundFromUrl);
        }

        var format = $("input[name='export-format']:checked").val();
        var originalHtml = button.html();
        paramsObj.set('format', format);
        var params = paramsObj.toString();

        button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span> ' + (window.gettext ? window.gettext('Processing...') : 'Processing...'));

        $.ajax({
            url: url + "?" + params,
            type: 'GET',
            headers: getHeader(),
            success: function(data) {
                if (exportModal) exportModal.hide();

                if (url.includes('center')) {
                    // Centers use direct download sometimes or zip name return
                    if (data.length > 5) {
                         window.open("/mscc/export-download/" + data, "_blank");
                         showModal(window.gettext ? window.gettext('Export successful. Your download should start automatically.') : 'Export successful. Your download should start automatically.');
                    } else {
                         showModal(window.gettext ? window.gettext('Export started successfully. You will be notified when the file is ready.') : 'Export started successfully. You will be notified when the file is ready.');
                    }
                } else {
                    showModal(window.gettext ? window.gettext('Export started successfully. Processing may take a few minutes depending on the data size.') : 'Export started successfully. Processing may take a few minutes depending on the data size.');
                    pollExportStatus(data.export_id, 90);
                }
            },
            error: function() {
                showModal(window.gettext ? window.gettext('Failed to start export. Please try again later.') : 'Failed to start export. Please try again later.');
            },
            complete: function() {
                button.prop('disabled', false).html(originalHtml);
            }
        });
    }

    // Start Export for Beneficiaries
    $(document).on('click', '#exportOptionsModal .start-export', function() {
        initiateExport($(this), "/mscc/export-list-background/", true);
    });

    // Start Export for Centers
    $(document).on('click', '#exportOptionsModal .start-export-center', function() {
        initiateExport($(this), "/locations/export-center-background/", false);
    });

    // Start Export for Teachers
    $(document).on('click', '#exportOptionsModal .start-export-teacher', function() {
        const button = $(this);
        const originalHtml = button.html();
        const params = $('#filter-form').serialize();
        const exportUrl = params ? ("/students/teacher-export/?" + params) : "/students/teacher-export/";

        button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span> ' + (window.gettext ? window.gettext('Processing...') : 'Processing...'));

        $.ajax({
            url: exportUrl,
            type: "GET",
            headers: getHeader(),
            success: function(data) {
                if (exportModal) exportModal.hide();

                const fileName = (data || '').toString().trim();
                if (fileName.length > 0) {
                    window.open("/mscc/export-download-csv/" + encodeURIComponent(fileName), "_blank");
                    showModal(window.gettext ? window.gettext('Teacher export completed. Your download should start automatically.') : 'Teacher export completed. Your download should start automatically.');
                } else {
                    showModal(window.gettext ? window.gettext('Teacher export completed, but no file was returned.') : 'Teacher export completed, but no file was returned.');
                }
            },
            error: function() {
                showModal(window.gettext ? window.gettext('Failed to export teacher data. Please try again later.') : 'Failed to export teacher data. Please try again later.');
            },
            complete: function() {
                button.prop('disabled', false).html(originalHtml);
            }
        });
    });

    // Active Filters Display Logic
    function updateActiveFilters() {
        const $container = $('#active-filters');
        if (!$container.length) return;
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
