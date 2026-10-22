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
            var isBLN = programme.value === 'BLN';
            // The server derives the BLN grade from the saved Education Service Program.
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
            if (isBLN && choices.length === 1) {
                grade.value = String(choices[0].id);
            }

            var message = helpByProgramme[programme.value] || helpByProgramme[''] || '';
            if (help) help.textContent = message;
            // Keep missing Education Service information visible to browser validation.
            grade.disabled = false;
            grade.setCustomValidity(isBLN && !choices.length ? message : '');
        }

        programme.addEventListener('change', updateGrades);
        updateGrades();
    }

    function initializeResidenceChoices() {
        var form = document.getElementById('exceptional-exam-form');
        if (!form) return;

        // Residence parents and village choices are supplied by the server
        // from the child's registration. Keep the parents read-only.
        ['governorate', 'district', 'nearest_town'].forEach(function (name) {
            var field = form.elements[name];
            if (!field) return;
            var descriptions = (field.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
            if (descriptions.indexOf('residence-selection-help') === -1) {
                descriptions.push('residence-selection-help');
            }
            field.setAttribute('aria-describedby', descriptions.join(' '));
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
