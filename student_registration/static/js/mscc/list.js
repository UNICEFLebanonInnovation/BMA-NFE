
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

    // Common Export Handler Function
    function initiateExport(button, url, checkRound = false) {
        // Build export params from the current URL first so active filters are preserved
        // even when the offcanvas filter form has not been interacted with.
        var paramsObj = new URLSearchParams(window.location.search || '');
        var formSerialized = $('#filter-form').serialize();
        if (formSerialized) {
            var formParams = new URLSearchParams(formSerialized);
            formParams.forEach(function(value, key) {
                paramsObj.set(key, value);
            });
        }

        var format = $("input[name='export-format']:checked").val();
        var originalHtml = button.html();
        paramsObj.set('format', format);
        var params = paramsObj.toString();

        button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span> Processsing...');

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
                         showModal('Export successful. Your download should start automatically.');
                    } else {
                         showModal('Export started successfully. You will be notified when the file is ready.');
                    }
                } else {
                    showModal('Export started successfully. Processing may take a few minutes depending on the data size. You will be notified when the file is ready.');
                }
            },
            error: function() {
                showModal('Failed to start export. Please try again later.');
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

        button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span> Processing...');

        $.ajax({
            url: "/students/teacher-export/",
            type: "GET",
            headers: getHeader(),
            success: function(data) {
                if (exportModal) exportModal.hide();

                const fileName = (data || '').toString().trim();
                if (fileName.length > 0) {
                    window.open("/mscc/export-download-csv/" + encodeURIComponent(fileName), "_blank");
                    showModal('Teacher export completed. Your download should start automatically.');
                } else {
                    showModal('Teacher export completed, but no file was returned.');
                }
            },
            error: function() {
                showModal('Failed to export teacher data. Please try again later.');
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
