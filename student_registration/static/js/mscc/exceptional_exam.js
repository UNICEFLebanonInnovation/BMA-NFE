(function () {
    'use strict';

    function initializeGradeChoices() {
        var form = document.getElementById('exceptional-exam-form');
        if (!form) return;

        var programme = form.elements.programme;
        var grade = form.elements.grade;
        var choicesData = document.getElementById('exceptional-exam-grade-choices');
        var helpData = document.getElementById('exceptional-exam-grade-help');
        var gradeField = document.getElementById('exceptional-exam-grade-field');
        if (!programme || !grade || !choicesData || !helpData || !gradeField) return;

        var choicesByProgramme;
        var helpByProgramme;
        try {
            choicesByProgramme = JSON.parse(choicesData.textContent);
            helpByProgramme = JSON.parse(helpData.textContent);
        } catch (error) {
            return;
        }
        if (!choicesByProgramme || !helpByProgramme) return;

        var placeholder = grade.options.length ? grade.options[0].text : form.getAttribute('data-select-prompt') || '';
        var help = gradeField.querySelector('.form-text');
        if (help) {
            help.id = help.id || 'exceptional-exam-grade-help-text';
            help.setAttribute('aria-live', 'polite');
            var descriptions = (grade.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
            if (descriptions.indexOf(help.id) === -1) descriptions.push(help.id);
            grade.setAttribute('aria-describedby', descriptions.join(' '));
        }

        function updateGrades() {
            // The server computes BLN eligibility from the registered child's age.
            var choices = choicesByProgramme[programme.value] || [];
            if (!Array.isArray(choices)) return;
            var previousGrade = grade.value;
            grade.innerHTML = '';
            grade.add(new Option(placeholder, ''));
            choices.forEach(function (choice) {
                grade.add(new Option(choice.text, String(choice.id)));
            });
            var stillAvailable = choices.some(function (choice) {
                return String(choice.id) === previousGrade;
            });
            grade.value = stillAvailable ? previousGrade : '';
            if (programme.value === 'BLN' && choices.length === 1) {
                grade.value = String(choices[0].id);
            }

            var message = helpByProgramme[programme.value] || helpByProgramme[''] || '';
            if (help) help.textContent = message;
            // Keep the required select enabled so an ineligible BLN application
            // cannot bypass the browser's validation when no grade is available.
            grade.disabled = false;
            grade.setCustomValidity(programme.value === 'BLN' && !choices.length ? message : '');
        }

        programme.addEventListener('change', updateGrades);
        updateGrades();
    }

    function initializeResidenceChoices() {
        var form = document.getElementById('exceptional-exam-form');
        if (!form) return;

        var optionsUrl = form.getAttribute('data-options-url');
        var governorate = form.elements.governorate;
        var district = form.elements.district;
        var nearestTown = form.elements.nearest_town;
        if (!optionsUrl || !governorate || !district || !nearestTown) return;

        var selectPrompt = form.getAttribute('data-select-prompt') || '';
        var districtPlaceholder = district.options.length ? district.options[0].text : selectPrompt;
        var villagePlaceholder = nearestTown.options.length ? nearestTown.options[0].text : selectPrompt;
        var districtStatus = document.getElementById('exceptional-exam-district-status');
        var villageStatus = document.getElementById('exceptional-exam-village-status');
        var districtRetry = document.getElementById('exceptional-exam-district-retry');
        var villageRetry = document.getElementById('exceptional-exam-village-retry');
        var districtRequest = { version: 0, controller: null };
        var villageRequest = { version: 0, controller: null };

        function locationMessages(type) {
            return {
                loading: form.getAttribute('data-' + type + '-loading') || '',
                empty: form.getAttribute('data-' + type + '-empty') || '',
                error: form.getAttribute('data-' + type + '-error') || ''
            };
        }

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
                loadChoices(district, governorate.value, '2', districtPlaceholder, districtRequest, districtStatus, districtRetry, locationMessages('district'));
            }
        }

        function updateVillages() {
            clearVillage();
            if (governorate.value && district.value) {
                loadChoices(nearestTown, district.value, 'village', villagePlaceholder, villageRequest, villageStatus, villageRetry, locationMessages('village'));
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

    function initializeExceptionalExam() {
        initializeGradeChoices();
        initializeResidenceChoices();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeExceptionalExam);
    } else {
        initializeExceptionalExam();
    }
}());
