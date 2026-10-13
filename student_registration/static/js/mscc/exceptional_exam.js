(function () {
    'use strict';

    function initializeResidenceChoices() {
        var form = document.getElementById('exceptional-exam-form');
        if (!form) return;

        var optionsUrl = form.getAttribute('data-options-url');
        var governorate = form.elements.governorate;
        var district = form.elements.district;
        var nearestTown = form.elements.nearest_town;
        if (!optionsUrl || !governorate || !district || !nearestTown) return;

        var districtPlaceholder = district.options.length ? district.options[0].text : 'Select / اختر';
        var villagePlaceholder = nearestTown.options.length ? nearestTown.options[0].text : 'Select / اختر';
        var districtStatus = document.getElementById('exceptional-exam-district-status');
        var villageStatus = document.getElementById('exceptional-exam-village-status');
        var districtRetry = document.getElementById('exceptional-exam-district-retry');
        var villageRetry = document.getElementById('exceptional-exam-village-retry');
        var districtRequest = { version: 0, controller: null };
        var villageRequest = { version: 0, controller: null };

        function replaceChoices(select, choices, placeholder, enabled) {
            select.innerHTML = '';
            select.add(new Option(placeholder, ''));
            choices.forEach(function (choice) {
                select.add(new Option(choice.text, String(choice.id)));
            });
            select.value = '';
            select.disabled = !enabled;
        }

        function describeSelect(select, statusId) {
            var describedBy = select.getAttribute('aria-describedby') || '';
            var descriptions = describedBy.split(/\s+/).filter(Boolean);
            ['residence-selection-help', statusId].filter(Boolean).forEach(function (id) {
                if (descriptions.indexOf(id) === -1) descriptions.push(id);
            });
            select.setAttribute('aria-describedby', descriptions.join(' '));
        }

        function setStatus(status, retry, message, isError) {
            if (status) {
                status.textContent = message;
                status.classList.toggle('text-danger', Boolean(isError));
                status.classList.toggle('text-muted', !isError);
            }
            if (retry) {
                retry.hidden = !isError;
                retry.classList.toggle('d-none', !isError);
            }
        }

        function cancelRequest(request) {
            request.version += 1;
            if (request.controller) {
                request.controller.abort();
                request.controller = null;
            }
        }

        function clearVillage() {
            cancelRequest(villageRequest);
            replaceChoices(nearestTown, [], villagePlaceholder, false);
            nearestTown.setAttribute('aria-busy', 'false');
            setStatus(villageStatus, villageRetry, '', false);
        }

        function loadChoices(select, parentId, type, placeholder, request, status, retry, messages) {
            cancelRequest(request);
            var version = request.version;
            replaceChoices(select, [], placeholder, false);
            select.setAttribute('aria-busy', 'true');
            setStatus(status, retry, messages.loading, false);

            var url = new URL(optionsUrl, window.location.href);
            url.searchParams.set('type', type);
            url.searchParams.set('parent', parentId);
            var fetchOptions = { credentials: 'same-origin', headers: { Accept: 'application/json' } };
            if (typeof AbortController !== 'undefined') {
                request.controller = new AbortController();
                fetchOptions.signal = request.controller.signal;
            }

            fetch(url.toString(), fetchOptions).then(function (response) {
                if (!response.ok) throw new Error('Location choices unavailable');
                return response.json();
            }).then(function (data) {
                if (version !== request.version) return;
                if (!data || !Array.isArray(data.results) || data.results.some(function (choice) {
                    return !choice || choice.id === null || choice.id === undefined || String(choice.id) === '' || typeof choice.text !== 'string';
                })) {
                    throw new Error('Invalid location choices');
                }
                replaceChoices(select, data.results, placeholder, data.results.length > 0);
                setStatus(status, retry, data.results.length ? '' : messages.empty, false);
            }).catch(function (error) {
                if (version !== request.version || error.name === 'AbortError') return;
                replaceChoices(select, [], placeholder, false);
                setStatus(status, retry, messages.error, true);
            }).finally(function () {
                if (version === request.version) {
                    request.controller = null;
                    select.setAttribute('aria-busy', 'false');
                }
            });
        }

        function updateDistricts() {
            cancelRequest(districtRequest);
            replaceChoices(district, [], districtPlaceholder, false);
            district.setAttribute('aria-busy', 'false');
            setStatus(districtStatus, districtRetry, '', false);
            clearVillage();
            if (governorate.value) {
                loadChoices(district, governorate.value, '2', districtPlaceholder, districtRequest, districtStatus, districtRetry, {
                    loading: 'Loading districts… / جارٍ تحميل الأقضية…',
                    empty: 'No districts are available for this governorate. / لا توجد أقضية متاحة لهذه المحافظة.',
                    error: 'Districts could not be loaded. Please retry. / تعذّر تحميل الأقضية. يرجى إعادة المحاولة.'
                });
            }
        }

        function updateVillages() {
            clearVillage();
            if (governorate.value && district.value) {
                loadChoices(nearestTown, district.value, 'village', villagePlaceholder, villageRequest, villageStatus, villageRetry, {
                    loading: 'Loading villages… / جارٍ تحميل القرى…',
                    empty: 'No villages are available for this district. / لا توجد قرى متاحة لهذا القضاء.',
                    error: 'Villages could not be loaded. Please retry. / تعذّر تحميل القرى. يرجى إعادة المحاولة.'
                });
            }
        }

        describeSelect(governorate);
        describeSelect(district, 'exceptional-exam-district-status');
        describeSelect(nearestTown, 'exceptional-exam-village-status');
        governorate.addEventListener('change', updateDistricts);
        district.addEventListener('change', updateVillages);
        if (districtRetry) districtRetry.addEventListener('click', updateDistricts);
        if (villageRetry) villageRetry.addEventListener('click', updateVillages);

        // Server choices already match the selected parents, including saved and bound forms.
        district.disabled = !governorate.value;
        nearestTown.disabled = !governorate.value || !district.value;
        if (!governorate.value) {
            replaceChoices(district, [], districtPlaceholder, false);
            replaceChoices(nearestTown, [], villagePlaceholder, false);
        } else if (!district.value) {
            replaceChoices(nearestTown, [], villagePlaceholder, false);
        }

        form.addEventListener('submit', function (event) {
            if (district.disabled || nearestTown.disabled) {
                event.preventDefault();
                if (districtRetry && !districtRetry.hidden) {
                    districtRetry.focus();
                } else if (villageRetry && !villageRetry.hidden) {
                    villageRetry.focus();
                } else if (district.disabled) {
                    governorate.focus();
                } else {
                    district.focus();
                }
            }
        });

        var errorSummary = document.getElementById('exceptional-exam-errors');
        if (errorSummary) errorSummary.focus();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeResidenceChoices);
    } else {
        initializeResidenceChoices();
    }
}());
