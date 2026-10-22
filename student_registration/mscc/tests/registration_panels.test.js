// Run with Node 18+: node --test student_registration/mscc/tests/registration_panels.test.js
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const template = fs.readFileSync(path.join(__dirname, '../../templates/mscc/main_form.html'), 'utf8');
const scripts = [...template.matchAll(/<script type="text\/javascript">([\s\S]*?)<\/script>/g)];
const wizardScript = scripts.at(-1)[1];

function panelsWithStyles(legacyStyles) {
    const panels = [1, 2, 3].map(step => ({
        id: 'step-' + step,
        classes: new Set(['step-content', step === 1 ? 'active' : 'd-none']),
        display: '',
    }));
    const unrelated = {id: 'unrelated-panel', classes: new Set(['step-content']), display: ''};
    const elements = new Map(panels.map(panel => ['#' + panel.id, panel]));
    function wrap(items) {
        const selection = {
            length: items.length,
            addClass(names) { items.forEach(item => names.split(' ').forEach(name => item.classes.add(name))); return selection; },
            removeClass(names) { items.forEach(item => names.split(' ').forEach(name => item.classes.delete(name))); return selection; },
            hide() { items.forEach(item => { item.display = 'none'; }); return selection; },
            show() { items.forEach(item => { item.display = 'block'; }); return selection; },
            filter(selector) { return wrap(items.filter(item => '#' + item.id === selector)); },
            css() { return selection; },
            on() { return selection; },
            animate() { return selection; },
            offset() { return {top: 100}; },
            val() { return ''; },
            is() { return false; },
            text(value) { return arguments.length ? selection : ''; },
            find() { return wrap([]); },
        };
        return selection;
    }
    function $(selector) {
        if (typeof selector === 'function') { selector(); return; }
        if (selector === '#registrationForm .step-content') return wrap(panels);
        if (selector === '.step-content') return wrap([...panels, unrelated]);
        if (!elements.has(selector)) {
            elements.set(selector, {id: selector, classes: new Set(), display: ''});
        }
        return wrap([elements.get(selector)]);
    }
    const context = vm.createContext({$, window: {}, document: {querySelectorAll: () => []}});
    vm.runInContext(wizardScript, context);
    function visible(panel) {
        if (panel.classes.has('d-none') || panel.display === 'none') return false;
        // Historical base.css hides these IDs even after d-none is removed.
        if (legacyStyles && panel.id !== 'step-1' && !panel.display) return false;
        return true;
    }
    return {panels, unrelated, show: context.window.updateWizard, visible};
}

for (const legacy of [false, true]) {
    const styles = legacy ? 'cached legacy CSS' : 'current CSS';
    test('Caregivers is the only visible and active panel with ' + styles, () => {
        const wizard = panelsWithStyles(legacy);
        wizard.show(2);
        assert.deepEqual(wizard.panels.map(wizard.visible), [false, true, false]);
        assert.deepEqual(wizard.panels.map(panel => panel.classes.has('active')), [false, true, false]);
    });

    test('Review containing Save becomes visible with ' + styles, () => {
        const wizard = panelsWithStyles(legacy);
        wizard.show(2);
        wizard.show(3);
        assert.deepEqual(wizard.panels.map(wizard.visible), [false, false, true]);
        assert.deepEqual(wizard.panels.map(panel => panel.classes.has('active')), [false, false, true]);
    });

    test('Previous returns to Caregivers and Identity with ' + styles, () => {
        const wizard = panelsWithStyles(legacy);
        wizard.show(3);
        wizard.show(2);
        assert.deepEqual(wizard.panels.map(wizard.visible), [false, true, false]);
        wizard.show(1);
        assert.deepEqual(wizard.panels.map(wizard.visible), [true, false, false]);
        assert.equal(wizard.unrelated.display, '');
        assert.equal(wizard.unrelated.classes.has('d-none'), false);
    });
}
