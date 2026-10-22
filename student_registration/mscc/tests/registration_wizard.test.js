// Run with: node --test student_registration/mscc/tests/registration_wizard.test.js
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../../static/js/mscc/mscc.js'), 'utf8');

function wizard() {
    const values = new Map(Object.entries({
        '#id_child_first_name': 'آدم', '#id_child_father_name': 'بسام',
        '#id_child_last_name': 'العلي', '#id_child_mother_fullname': 'مريم',
        '#id_child_gender': 'Male', '#id_child_nationality': '1',
        '#id_child_birthday_year': '2015', '#id_child_birthday_month': '3',
        '#id_child_birthday_day': '12', '#id_child_disability': '1',
        '#id_child_governorate': '1', '#id_child_district': '2',
        '#id_child_cadaster': '3', '#id_child_village': 'achrafieh',
        '#id_child_country_of_birth': 'LB', '#id_child_place_of_birth': 'بيروت',
        '#id_nfe_programme': 'BLN Level 1',
    }));
    const properties = new Map();
    const requests = [];
    const errors = [];
    let summaries = 0;
    // Supply the DOM surface used by these isolated validation/AJAX tests.
    // Full rendering, required markers and navigation are checked in Chromium.
    function $(selector) {
        const element = {
            length: values.has(selector) ? 1 : 0,
            ready() { return element; },
            val(value) {
                if (arguments.length) { values.set(selector, value); return element; }
                return values.get(selector);
            },
            prop(name, value) {
                const key = selector + ':' + name;
                if (arguments.length > 1) { properties.set(key, value); return element; }
                return properties.get(key);
            },
            is() { return values.has(selector); },
            text() { return values.get(selector + ':text') || ''; },
            attr(name, value) {
                if (arguments.length > 1) return element;
                return name === 'id' ? String(selector).replace(/^#/, '') : undefined;
            },
            each(callback) {
                if (Array.isArray(selector)) selector.forEach((value, index) => callback(index, value));
                return element;
            },
        };
        for (const method of ['hide', 'show', 'closest', 'siblings', 'find', 'remove', 'removeClass', 'addClass', 'toggleClass', 'empty', 'prepend', 'append', 'html']) {
            element[method] = () => element;
        }
        return element;
    }
    $.ajax = options => {
        const request = {...options, aborted: false, abort() { this.aborted = true; }};
        requests.push(request);
        return request;
    };
    const context = vm.createContext({$, document: {}, window: {location: {pathname: '/mscc/child-add/'}}, console, getHeader: () => ({})});
    vm.runInContext(source, context);
    context.clearErrors = () => { errors.length = 0; };
    context.showError = selector => errors.push(selector);
    context.showFormValidationErrors = () => { summaries += 1; };
    return {context, values, requests, errors, properties, summaries: () => summaries};
}

const duplicate = {result: [{id: 1, center__name: 'Test centre'}]};

test('completed Identity fields allow Next without removed address fields', () => {
    const {context, errors} = wizard();
    assert.equal(context.validateMainForm(true, 1), true);
    assert.deepEqual(errors, []);
});

for (const field of ['child_country_of_birth', 'child_place_of_birth', 'child_village', 'nfe_programme']) {
    test('a missing ' + field + ' shows the Identity error summary', () => {
        const state = wizard();
        state.values.set('#id_' + field, '');
        assert.equal(state.context.validateMainForm(true, 1), false);
        assert(state.errors.includes('#id_' + field));
        assert.equal(state.summaries(), 1);
    });
}

test('missing Other details show the error summary and filling them allows Next', () => {
    const state = wizard();
    state.values.set('#id_child_nationality', '6');
    state.values.set('#id_child_nationality_other', '');
    assert.equal(state.context.validateMainForm(true, 1), false);
    assert(state.errors.includes('#id_child_nationality_other'));
    assert.equal(state.summaries(), 1);
    state.values.set('#id_child_nationality_other', 'جنسيّة أخرى');
    assert.equal(state.context.validateMainForm(true, 1), true);
});

test('an obsolete duplicate result cannot disable Next after a newer clear result', () => {
    const state = wizard();
    state.context.child_duplication_check();
    state.values.set('#id_child_first_name', 'سليم');
    state.context.child_duplication_check();
    assert.equal(state.requests[0].aborted, true);
    state.requests[1].success({result: []});
    // Cancellation can race with completion; deliver the older callback anyway.
    state.requests[0].success(duplicate);
    assert.equal(state.context.isDuplicateFound, false);
    assert.equal(state.properties.get('#next-btn:disabled'), false);
    assert.equal(state.properties.get('#submit-id-save:disabled'), false);
});

test('the current duplicate is blocked and corrected identity clears it', () => {
    const state = wizard();
    state.context.child_duplication_check();
    state.requests[0].success(duplicate);
    assert.equal(state.context.isDuplicateFound, true);
    assert.equal(state.properties.get('#next-btn:disabled'), true);
    state.values.set('#id_child_first_name', 'سليم');
    state.context.child_duplication_check();
    state.requests[1].success({result: []});
    assert.equal(state.context.isDuplicateFound, false);
    assert.equal(state.properties.get('#next-btn:disabled'), false);
});

test('incomplete identity clears the duplicate and cancels its pending check', () => {
    const state = wizard();
    state.context.child_duplication_check();
    state.requests[0].success(duplicate);
    state.values.set('#id_child_first_name', '');
    state.context.child_duplication_check();
    assert.equal(state.requests.length, 1);
    assert.equal(state.requests[0].aborted, true);
    state.requests[0].success(duplicate);
    assert.equal(state.context.isDuplicateFound, false);
    assert.equal(state.properties.get('#next-btn:disabled'), false);
});

test('potential-match prefill invalidates duplicate results for the old identity', () => {
    const state = wizard();
    state.values.set('#registrationForm', 'present');
    state.context.child_duplication_check();
    state.context.fill_old_child_data([{child_first_name: 'سليم'}]);
    assert.equal(state.requests.length, 2);
    assert.equal(state.requests[0].aborted, true);
    assert.equal(JSON.parse(state.requests[1].data).first_name, 'سليم');
    state.requests[1].success({result: []});
    state.requests[0].success(duplicate);
    assert.equal(state.context.isDuplicateFound, false);
    assert.equal(state.properties.get('#next-btn:disabled'), false);
});

test('conditional requirements follow the current selections after a prefill or reset', () => {
    const state = wizard();
    state.values.set('#registrationForm', 'present');
    state.values.set('#id_child_nationality', '6');
    state.values.set('#id_child_disability option:selected:text', 'غير ذلك');
    state.context.updateConditionalRequirements();
    assert.equal(state.properties.get('#id_child_nationality_other:required'), true);
    assert.equal(state.properties.get('#id_child_disability_other:required'), true);
    state.values.set('#id_child_nationality', '1');
    state.values.set('#id_child_disability option:selected:text', 'None');
    state.context.updateConditionalRequirements();
    assert.equal(state.properties.get('#id_child_nationality_other:required'), false);
    assert.equal(state.properties.get('#id_child_disability_other:required'), false);
});
