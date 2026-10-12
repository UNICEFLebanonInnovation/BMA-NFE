(function () {
    'use strict';

    function initializeResidenceChoices() {
        var form = document.getElementById('exceptional-exam-form');
        var catalogElement = document.getElementById('exceptional-exam-residence-catalog');
        if (!form || !catalogElement) return;

        var catalog = JSON.parse(catalogElement.textContent);
        var governorate = form.elements.governorate;
        var district = form.elements.district;
        var nearestTown = form.elements.nearest_town;
        if (!governorate || !district || !nearestTown) return;

        var districtPlaceholder = district.options.length ? district.options[0].text : 'Select / اختر';
        var townPlaceholder = nearestTown.options.length ? nearestTown.options[0].text : 'Select / اختر';
        var initialDistrict = district.value;
        var initialTown = nearestTown.value;

        function replaceChoices(select, choices, selectedValue, placeholder, enabled) {
            select.innerHTML = '';
            select.add(new Option(placeholder, ''));
            choices.forEach(function (choice) {
                select.add(new Option(choice[1], choice[0]));
            });
            select.value = selectedValue || '';
            if (select.selectedIndex === -1) select.value = '';
            select.disabled = !enabled;
            var describedBy = select.getAttribute('aria-describedby') || '';
            if (describedBy.split(/\s+/).indexOf('residence-selection-help') === -1) {
                select.setAttribute('aria-describedby', (describedBy + ' residence-selection-help').trim());
            }
        }

        function updateTowns(selectedValue) {
            var governorateData = catalog[governorate.value];
            var districtData = governorateData && governorateData.districts[district.value];
            replaceChoices(nearestTown, districtData ? districtData.towns : [], selectedValue, townPlaceholder, Boolean(districtData));
        }

        function updateDistricts(selectedValue, selectedTown) {
            var governorateData = catalog[governorate.value];
            var choices = [];
            if (governorateData) {
                Object.keys(governorateData.districts).forEach(function (code) {
                    choices.push([code, governorateData.districts[code].label]);
                });
            }
            replaceChoices(district, choices, selectedValue, districtPlaceholder, Boolean(governorateData));
            updateTowns(selectedTown);
        }

        governorate.addEventListener('change', function () {
            updateDistricts('', '');
        });
        district.addEventListener('change', function () {
            updateTowns('');
        });

        // Restore valid saved or submitted values after rebuilding dependent choices.
        updateDistricts(initialDistrict, initialTown);
        var errorSummary = document.getElementById('exceptional-exam-errors');
        if (errorSummary) errorSummary.focus();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeResidenceChoices);
    } else {
        initializeResidenceChoices();
    }
}());
