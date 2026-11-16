const { start } = require('./lib');
const path = require('path');
const S = path.join(__dirname, '..');
const PW = 'Nfe@Demo2026!';
const today = new Date().toISOString().slice(0, 10);
const DATA = {
  en: { first: 'رامي', father: 'نبيل', last: 'عساف', mother: 'ريما خليل', place: 'Beirut', phone: '03-456789',
        cg: ['سمير', 'أحمد', 'ناصر', 'أمل ناصر'], teacher: ['لينا', 'جورج', 'خوري', 'منى خوري'], alp: ['ليان', 'خالد', 'شاهين', 'هدى شاهين'],
        dup: ['هبة', 'بسام', 'درويش', '10', '8', '2016'] },
  ar: { first: 'كريم', father: 'وليد', last: 'حداد', mother: 'سلوى حداد', place: 'بيروت', phone: '03-456790',
        cg: ['سمير', 'أحمد', 'ناصر', 'أمل ناصر'], teacher: ['لينا', 'جورج', 'خوري', 'منى خوري'], alp: ['جنى', 'عماد', 'حمود', 'رنا حمود'],
        dup: ['هبة', 'بسام', 'درويش', '10', '8', '2016'] },
};
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
async function step(name, fn) { if (process.env.ONLY && !/^(nfe_|alp_)/.test(name) && !process.env.ONLY.split(',').includes(name)) return; try { await fn(); } catch (e) { console.log('ERR[' + name + ']', e.message.split('\n').slice(0, 4).join(' / ')); } }
async function submit(page) { const b = page.locator('form button[type="submit"]:visible, form input[type="submit"]:visible').last(); await b.click(); await page.waitForLoadState('networkidle'); await sleep(600); }
async function selectFirst(page, sel) { const v = await page.locator(sel + ' option').evaluateAll(os => (os.find(o => o.value) || {}).value); if (v) await page.selectOption(sel, v); return v; }
async function wait(page, ms = 700) { await page.waitForLoadState('networkidle'); await sleep(ms); }

async function nfe(lang) {
  const D = DATA[lang];
  const s = await start(lang); const { page } = s;
  await step('login', async () => {
    await s.goto('/accounts/login/'); await s.setLang(lang); await s.goto('/accounts/login/');
    await s.shot('00_login_empty');
    await page.fill('input[name="login"]', 'nfe.center'); await page.fill('input[name="password"]', PW);
    await s.shot('00_login_filled');
    await page.click('button[type="submit"]'); await wait(page, 1200); await s.setLang(lang); await s.goto('/landing-page/', 1500);
    await s.shot('nfe_01_home'); await s.shot('nfe_01_home_full', { full: true });
    await page.click('button:has(i.bi-globe)'); await sleep(400); await s.shot('nfe_02_language_menu');
    await page.keyboard.press('Escape'); await page.locator('header .dropdown').last().locator('button').click(); await sleep(400); await s.shot('nfe_03_user_menu');
    await page.keyboard.press('Escape');
  });
  await step('list', async () => {
    await s.goto('/mscc/list/', 1000); await s.shot('nfe_10_list'); await s.shot('nfe_10_list_full', { full: true });
    await page.click('button[data-bs-target="#filterOffcanvas"]'); await sleep(600); await s.shot('nfe_11_list_search');
    await page.keyboard.press('Escape'); await sleep(700);
    await page.locator('table [data-bs-toggle="dropdown"]').first().click(); await sleep(400); await s.shot('nfe_12_list_actions');
    await page.keyboard.press('Escape'); await sleep(300);
    await page.click('.download-report-async'); await sleep(800); await s.shot('nfe_13_export_modal');
    await page.keyboard.press('Escape'); await sleep(300);
  });
  let regId = null;
  await step('register', async () => {
    await s.goto('/mscc/child-add/', 1000); await s.shot('nfe_20_reg_step1_empty', { full: true });
    // duplicate check demonstration
    await page.fill('#id_child_first_name', D.dup[0]); await page.fill('#id_child_father_name', D.dup[1]); await page.fill('#id_child_last_name', D.dup[2]);
    await page.selectOption('#id_child_birthday_day', D.dup[3]); await page.selectOption('#id_child_birthday_month', D.dup[4]); await page.selectOption('#id_child_birthday_year', D.dup[5]);
    await sleep(2500); await s.shot('nfe_21_reg_duplicate_warning');
    await page.fill('#id_child_first_name', D.first); await page.fill('#id_child_father_name', D.father); await page.fill('#id_child_last_name', D.last);
    await page.selectOption('#id_child_birthday_day', '12'); await page.selectOption('#id_child_birthday_month', '3'); await page.selectOption('#id_child_birthday_year', '2014');
    await page.selectOption('#id_child_country_of_birth', 'LB'); await page.fill('#id_child_place_of_birth', D.place);
    await page.selectOption('#id_child_gender', 'Male'); await page.fill('#id_child_mother_fullname', D.mother);
    await page.selectOption('#id_child_nationality', '2'); await page.selectOption('#id_nfe_programme', 'BLN Level 2');
    await page.setInputFiles('#id_child_photo', path.join(S, 'sample_photo.jpg'));
    await page.selectOption('#id_child_governorate', '1'); await sleep(1500); await page.selectOption('#id_child_district', '2'); await sleep(1500);
    await selectFirst(page, '#id_child_cadaster'); await sleep(800); await selectFirst(page, '#id_child_village');
    await page.selectOption('#id_child_disability', '1'); await sleep(2500);
    await s.shot('nfe_22_reg_step1_filled', { full: true });
    await page.click('#next-btn'); await sleep(800); await s.shot('nfe_23_reg_step2_empty', { full: true });
    await page.fill('#id_first_phone_number', D.phone); await s.shot('nfe_24_reg_step2_filled', { full: true });
    await page.click('#next-btn'); await sleep(800); await s.shot('nfe_25_reg_step3_review', { full: true });
    await page.click('#submit-id-save'); await wait(page, 1500);
    await s.shot('nfe_26_reg_submitted', { full: true });
    const m = page.url().match(/child-profile\/(\d+)/); if (m) regId = m[1];
  });
  if (!regId) { await s.goto('/mscc/list/'); const href = await page.locator('a[href*="/mscc/child-profile/"]').first().getAttribute('href'); regId = href.match(/(\d+)/)[1]; }
  await step('profile', async () => {
    await s.goto(`/mscc/child-profile/${regId}/`, 1200); await s.shot('nfe_30_profile_header'); await s.shot('nfe_30_profile_full', { full: true });
    await page.click('#edu-tab'); await sleep(600); await s.shot('nfe_31_profile_education_tab', { full: true });
    await page.click('#attendance-tab'); await sleep(600); await s.shot('nfe_32_profile_attendance_tab', { full: true });
    await page.click('#exceptional-exam-tab'); await sleep(600); await s.shot('nfe_33_profile_exam_tab', { full: true });
    await s.goto(`/mscc/new-round/${regId}/`, 1000); await s.shot('nfe_34_new_round_form', { full: true });
  });
  await step('education', async () => {
    await s.goto(`/mscc/services/education-add/${regId}/`, 1000); await s.shot('nfe_40_education_form_empty', { full: true });
    await selectFirst(page, '#id_education_status'); await sleep(500); await selectFirst(page, '#id_round'); await sleep(500);
    await page.selectOption('#id_education_program', 'BLN Level 2'); await sleep(500);
    await page.selectOption('#id_class_section', 'A'); await page.fill('#id_registration_date', today);
    await s.shot('nfe_41_education_form_filled', { full: true });
    await submit(page); await sleep(800); await s.shot('nfe_42_education_saved', { full: true });
  });
  await step('exam', async () => {
    await s.goto(`/mscc/exceptional-exam/${regId}/`, 1000); await s.shot('nfe_50_exam_form_empty', { full: true });
    for (const [sel, v] of [['#id_governorate', '1'], ['#id_district', '2'], ['#id_country_of_birth', 'LB'], ['#id_programme', 'BLN Level 2']]) { if (await page.locator(sel + ':enabled').count()) { await page.selectOption(sel, v); await sleep(1000); } }
    if (await page.locator('#id_nearest_town:enabled').count()) await selectFirst(page, '#id_nearest_town');
    if (await page.locator('#id_place_of_birth:enabled').count()) await page.fill('#id_place_of_birth', D.place);
    if (await page.locator('#id_grade:enabled').count()) await selectFirst(page, '#id_grade');
    await page.selectOption('#id_math_language', 'ar'); await page.selectOption('#id_language_exam', 'en');
    await s.shot('nfe_51_exam_form_filled', { full: true });
    await submit(page); await sleep(800); await s.shot('nfe_52_exam_saved', { full: true });
  });
  await step('photo', async () => {
    await s.goto(`/mscc/photo-upload/${regId}/`, 800); await page.setInputFiles('#id_photo', path.join(S, 'sample_photo.jpg')); await sleep(600);
    await s.shot('nfe_60_photo_upload'); await submit(page); await sleep(800); await s.shot('nfe_61_photo_saved');
  });
  await step('edit', async () => { await s.goto(`/mscc/child-edit/${regId}/`, 1000); await s.shot('nfe_62_edit_profile', { full: true }); });
  await step('attendance', async () => {
    await s.goto('/mscc/attendance/', 1000); await s.shot('nfe_70_attendance_page');
    let loaded = false;
    for (const prog of ['BLN Level 1', 'BLN Level 2', 'BLN Level 3']) { for (const sec of ['A', 'B']) {
      await page.selectOption('#education_program', prog); await page.selectOption('#round', '2'); await page.selectOption('#class_section', sec);
      await page.click('#load_attendance_children'); await wait(page, 1500);
      if (await page.locator('#attendance_children .registration_id').count() > 1) { loaded = true; break; }
    } if (loaded) break; }
    await s.shot('nfe_71_attendance_loaded', { full: true });
    const labels = page.locator('#attendance_children label.btn-outline-danger');
    const n = await labels.count();
    for (let i = 0; i < Math.min(2, n); i++) { await labels.nth(i).click(); await sleep(300); const id = (await labels.nth(i).getAttribute('for')).replace(/^status_no_(new_)?/, ''); try { await page.selectOption('#absence_reason_' + id, i ? 'Transportation' : 'Sick'); } catch (e) {} }
    await s.shot('nfe_72_attendance_marked', { full: true });
    await page.click('#save_attendance_children'); await wait(page, 1500); await s.shot('nfe_73_attendance_saved', { full: true });
    await page.keyboard.press('Escape'); await sleep(800); try { await page.locator('.modal.show .btn').first().click({ timeout: 2000 }); } catch (e) {} await sleep(600);
    await page.evaluate(() => document.querySelector('label[for="day_off"]').click()); await sleep(500); await selectFirst(page, '#close_reason'); await sleep(300); await s.shot('nfe_74_attendance_day_off');
    await page.evaluate(() => document.querySelector('label[for="working_day"]').click());
  });
  await step('teachers', async () => {
    await s.goto('/mscc/teachers/', 1000); await s.shot('nfe_80_teachers_list', { full: true });
    await s.goto('/mscc/teacher-add/', 1000); await s.shot('nfe_81_teacher_form_empty', { full: true });
    await page.fill('#id_first_name', D.teacher[0]); await page.fill('#id_father_name', D.teacher[1]); await page.fill('#id_last_name', D.teacher[2]); await page.fill('#id_mother_fullname', D.teacher[3]);
    await page.selectOption('#id_sex', 'Female'); try { await page.fill('#id_birthdate', '1991-04-12'); } catch (e) {}
    await page.selectOption('#id_nationality', '1'); await page.selectOption('#id_id_type', '2'); await page.fill('#id_id_number', '000123456');
    await page.fill('#id_primary_phone_number', '03-111222'); await page.locator('input[name="trainings"]').first().check(); await page.fill('#id_email', 'lina@example.org'); await page.selectOption('#id_center', '1'); await page.selectOption('#id_round', '2');
    await page.check('#id_subjects_provided_0'); await page.check('#id_subjects_provided_1'); await page.check('#id_registration_level_0'); await page.fill('#id_years_of_experience', '5'); await page.selectOption('#id_extra_coaching', 'no');
    await s.shot('nfe_82_teacher_form_filled', { full: true }); await submit(page); await sleep(800); await s.shot('nfe_83_teacher_saved', { full: true });
    const edit = page.locator('a[href*="/mscc/teacher-edit/"]').last(); if (await edit.count()) { await s.goto(await edit.getAttribute('href'), 1000); await s.shot('nfe_84_teacher_edit', { full: true }); }
  });
  await step('centers', async () => { await s.goto('/locations/center-list/', 1000); if (!/404/.test(await page.title())) await s.shot('nfe_85_centers_list', { full: true }); });
  await step('dashboards', async () => {
    for (const [n, u] of [['nfe_90_dashboard', '/mscc/dashboard/'], ['nfe_91_learning_outcome', '/mscc/wellbeing-dashboard/'], ['nfe_92_teacher_dashboard', '/mscc/teacher-dashboard/'], ['nfe_93_attendance_heatmap', '/mscc/attendance-heatmap/'], ['nfe_94_centers_map', '/dashboard/centers-map/'], ['nfe_95_pivot_builder', '/dashboard/pivot-dashboard/']]) {
      await step(n, async () => { await s.goto(u, 2500); await s.shot(n, { full: true }); });
    }
  });
  await step('export', async () => {
    await s.goto('/mscc/list/', 1000); await page.click('.download-report-async'); await sleep(800);
    await page.locator('#exportOptionsModal button[type="submit"], #exportOptionsModal .btn-primary').last().click(); await wait(page, 4000); await s.shot('nfe_14_export_started');
    await page.keyboard.press('Escape'); await sleep(300); await page.locator('header .export-history-dropdown button').click(); await sleep(600); await s.shot('nfe_15_export_history');
    await page.keyboard.press('Escape');
  });
  await step('account', async () => {
    await s.goto('/users/partner', 800); await s.shot('nfe_96_profile_page', { full: true });
    await s.goto('/accounts/password/change/', 800); await s.shot('nfe_97_change_password', { full: true });
    await s.goto('/accounts/logout/', 800); await s.shot('nfe_98_logout');
  });
  await s.close();
}

async function alp(lang) {
  const D = DATA[lang];
  const s = await start(lang); const { page } = s;
  await step('login', async () => {
    await s.goto('/accounts/login/'); await s.setLang(lang); await s.login('alp.school', PW); await s.setLang(lang);
    await s.goto('/alp/landing-page/', 1500); await s.shot('alp_01_home'); await s.shot('alp_01_home_full', { full: true });
    await page.click('button:has(i.bi-globe)'); await sleep(400); await s.shot('alp_02_language_menu');
    await page.keyboard.press('Escape'); await page.locator('header .dropdown').last().locator('button').click(); await sleep(400); await s.shot('alp_03_user_menu'); await page.keyboard.press('Escape');
  });
  await step('list', async () => {
    await s.goto('/alp/registrations/', 1000); await s.shot('alp_10_list'); await s.shot('alp_10_list_full', { full: true });
    await page.click('button[data-bs-target="#filterOffcanvas"]'); await sleep(600); await s.shot('alp_11_list_search');
    await page.keyboard.press('Escape'); await sleep(700);
    const dd = page.locator('table [data-bs-toggle="dropdown"]').first(); if (await dd.count()) { await dd.click(); await sleep(400); await s.shot('alp_12_list_actions'); await page.keyboard.press('Escape'); }
    const ex = page.locator('.download-report-async, [data-bs-target="#exportOptionsModal"]'); if (await ex.count()) { await ex.click(); await sleep(600); await s.shot('alp_13_export_modal'); await page.keyboard.press('Escape'); }
  });
  let regId = null;
  await step('register', async () => {
    await s.goto('/alp/registrations/add/', 1000); await s.shot('alp_20_reg_step1_empty', { full: true });
    await page.fill('#id_child_first_name', D.alp[0]); await page.fill('#id_child_father_name', D.alp[1]); await page.fill('#id_child_last_name', D.alp[2]);
    await page.selectOption('#id_child_birthday_day', '5'); await page.selectOption('#id_child_birthday_month', '9'); await page.selectOption('#id_child_birthday_year', '2012');
    await page.selectOption('#id_child_gender', 'Female'); await page.fill('#id_child_mother_fullname', D.alp[3]); await page.selectOption('#id_child_nationality', '2');
    await page.setInputFiles('#id_child_photo', path.join(S, 'sample_photo.jpg'));
    await page.selectOption('#id_source_of_identification', 'BLN programme'); await page.selectOption('#id_child_living_arrangement', 'Living with caregivers');
    await page.selectOption('#id_child_disability', '1'); await page.selectOption('#id_child_marital_status', 'Single'); await page.selectOption('#id_child_have_children', 'No');
    await sleep(2500); await s.shot('alp_21_reg_step1_filled', { full: true });
    await page.click('#next-btn'); await sleep(800); await s.shot('alp_22_reg_step2_empty', { full: true });
    await page.selectOption('#id_child_have_sibling', 'Yes'); await page.selectOption('#id_child_siblings_have_disability', 'No'); await page.selectOption('#id_child_mother_pregnant_expecting', 'No');
    await selectFirst(page, '#id_father_educational_level'); await selectFirst(page, '#id_mother_educational_level');
    await page.fill('#id_first_phone_number', D.phone); await page.fill('#id_first_phone_number_confirm', D.phone); await page.selectOption('#id_first_phone_owner', 'Phone Main Caregiver');
    await page.fill('#id_children_number_under18', '3'); await page.selectOption('#id_main_caregiver', 'Father');
    await page.fill('#id_caregiver_first_name', D.cg[0]); await page.fill('#id_caregiver_middle_name', D.cg[1]); await page.fill('#id_caregiver_last_name', D.cg[2]); await page.fill('#id_caregiver_mother_name', D.cg[3]);
    await page.selectOption('#id_main_caregiver_nationality', '2'); await page.selectOption('#id_id_type', '1'); await sleep(500);
    for (const f of ['case_number', 'case_number_confirm']) { try { await page.fill('#id_' + f, '245-19C12345'); } catch (e) {} }
    for (const f of ['parent_individual_case_number', 'parent_individual_case_number_confirm']) { try { await page.fill('#id_' + f, '245-12345601'); } catch (e) {} }
    for (const f of ['individual_case_number', 'individual_case_number_confirm']) { try { await page.fill('#id_' + f, '245-12345603'); } catch (e) {} }
    for (const f of ['recorded_number', 'recorded_number_confirm']) { try { await page.fill('#id_' + f, '1234567'); } catch (e) {} }
    await s.shot('alp_23_reg_step2_filled', { full: true });
    await page.click('#next-btn'); await sleep(800); await s.shot('alp_24_reg_step3_empty', { full: true });
    await page.fill('#id_registration_date', today); await page.selectOption('#id_round', '2'); await page.selectOption('#id_programme', '2'); await page.selectOption('#id_section', '1');
    await page.setInputFiles('#id_consent_form', path.join(S, 'sample_consent.jpg')); await page.selectOption('#id_have_labour', 'No'); await page.check('#id_cash_support_programmes_0');
    await s.shot('alp_25_reg_step3_filled', { full: true });
    await page.click('#submit-id-save'); await wait(page, 1500); await s.shot('alp_26_reg_submitted', { full: true });
    const m = page.url().match(/child-profile\/(\d+)/); if (m) regId = m[1];
  });
  if (!regId) { await s.goto('/alp/registrations/'); const href = await page.locator('a[href*="/alp/child-profile/"]').first().getAttribute('href'); regId = href.match(/(\d+)/)[1]; }
  await step('profile', async () => {
    await s.goto(`/alp/child-profile/${regId}/`, 1200); await s.shot('alp_30_profile_header'); await s.shot('alp_30_profile_full', { full: true });
    const tabs = page.locator('.nav-tabs button'); const tc = await tabs.count();
    for (let i = 1; i < Math.min(tc, 4); i++) { await tabs.nth(i).click(); await sleep(600); await s.shot(`alp_3${i}_profile_tab${i}`, { full: true }); }
    await s.goto(`/alp/registrations/edit/${regId}/`, 1000); await s.shot('alp_33_edit_registration', { full: true });
    await s.goto(`/alp/registrations/delete/${regId}/`, 800); await s.shot('alp_34_delete_confirm');
  });
  await step('attendance', async () => {
    await s.goto('/alp/attendance/', 1000); await s.shot('alp_40_attendance_page');
    let loaded = false;
    for (const prog of ['1', '2', '3']) { for (const sec of ['1', '2']) {
      await page.selectOption('#programme', prog); await page.selectOption('#round', '2'); await page.selectOption('#section', sec);
      await page.click('#load_attendance_children'); await wait(page, 1500);
      if (await page.locator('#attendance_children .registration_id').count() > 1) { loaded = true; break; }
    } if (loaded) break; }
    await s.shot('alp_41_attendance_loaded', { full: true });
    const labels = page.locator('#attendance_children label.btn-outline-danger'); const n = await labels.count();
    for (let i = 0; i < Math.min(2, n); i++) { await labels.nth(i).click(); await sleep(300); const id = (await labels.nth(i).getAttribute('for')).replace(/^status_no_(new_)?/, ''); try { await page.selectOption('#absence_reason_' + id, i ? 'Transportation' : 'Sick'); } catch (e) {} }
    await s.shot('alp_42_attendance_marked', { full: true });
    await page.click('#save_attendance_children'); await wait(page, 1500); await s.shot('alp_43_attendance_saved', { full: true });
    await page.keyboard.press('Escape'); await sleep(800); try { await page.locator('.modal.show .btn').first().click({ timeout: 2000 }); } catch (e) {} await sleep(600);
    await page.evaluate(() => document.querySelector('label[for="day_off"]').click()); await sleep(500); await selectFirst(page, '#close_reason'); await sleep(300); await s.shot('alp_44_attendance_day_off');
    await page.evaluate(() => document.querySelector('label[for="working_day"]').click());
  });
  await step('teacher_attendance', async () => {
    await s.goto('/alp/teacher-attendance/', 1000); await s.shot('alp_50_teacher_attendance_page', { full: true });
    await page.click('#load_attendance_teachers'); await wait(page, 1500); await s.shot('alp_51_teacher_attendance_loaded', { full: true });
    const lab = page.locator('#attendance_teachers label.btn-outline-danger, #attendance_teachers label.btn-outline-success'); if (await lab.count()) await lab.first().click();
    await s.shot('alp_52_teacher_attendance_marked', { full: true });
    await page.click('#save_attendance_teachers'); await wait(page, 1500); await s.shot('alp_53_teacher_attendance_saved', { full: true });
  });
  await step('teachers', async () => {
    await s.goto('/alp/teachers/', 1000); await s.shot('alp_60_teachers_list', { full: true });
    await s.goto('/alp/teachers/add/', 1000); await s.shot('alp_61_teacher_form_empty', { full: true });
    await page.fill('#id_first_name', D.teacher[0]); await page.fill('#id_father_name', D.teacher[1]); await page.fill('#id_last_name', D.teacher[2]); await page.fill('#id_mother_fullname', D.teacher[3]);
    await page.selectOption('#id_sex', 'Female'); await page.fill('#id_birthdate', '1991-04-12'); await page.selectOption('#id_nationality', '1');
    await page.fill('#id_phone_number', '03-111222'); await page.locator('input[name="trainings"]').first().check(); await page.fill('#id_email', 'lina@example.org'); await page.selectOption('#id_round', '2'); await page.selectOption('#id_teacher_assignment', 'ALP only');
    await page.fill('#id_teaching_hours_mscc', '12'); await page.check('#id_subjects_provided_0'); await page.check('#id_subjects_provided_2'); await page.check('#id_registration_level_1');
    await page.fill('#id_years_of_experience', '5'); await page.selectOption('#id_extra_coaching', 'no');
    await s.shot('alp_62_teacher_form_filled', { full: true }); await submit(page); await sleep(800); await s.shot('alp_63_teacher_saved', { full: true });
    const edit = page.locator('a[href*="/alp/teachers/edit/"]').last(); if (await edit.count()) { await s.goto(await edit.getAttribute('href'), 1000); await s.shot('alp_64_teacher_edit', { full: true }); }
  });
  await step('grading', async () => {
    await s.goto('/alp/grading/add/', 1000); await s.shot('alp_70_grading_form_empty', { full: true });
    await page.selectOption('#id_registration', regId); await page.fill('#id_grade_1', '15'); await page.fill('#id_grade_2', '12'); await page.fill('#id_grade_3', '17'); await page.fill('#id_grade_4', '14');
    await s.shot('alp_71_grading_form_filled', { full: true }); await submit(page); await sleep(800); await s.shot('alp_72_grading_saved', { full: true });
  });
  await step('school', async () => {
    await s.goto('/alp/school-profile/', 1000); await s.shot('alp_80_school_profile', { full: true });
    await page.fill('#id_land_phone_number', '01-123457'); await submit(page); await sleep(800); await s.shot('alp_81_school_profile_saved', { full: true });
  });
  await step('dashboards', async () => {
    for (const [n, u] of [['alp_90_registration_dashboard', '/alp/dashboard/registration/'], ['alp_91_teacher_dashboard', '/alp/dashboard/teacher/'], ['alp_92_attendance_dashboard', '/alp/dashboard/attendance/'], ['alp_93_school_dashboard', '/alp/dashboard/school/'], ['alp_94_pivot_builder', '/alp/dashboard/pivot/']]) {
      await step(n, async () => { await s.goto(u, 2500); await s.shot(n, { full: true }); });
    }
  });
  await step('account', async () => { await s.goto('/accounts/password/change/', 800); await s.shot('alp_97_change_password', { full: true }); });
  await s.close();
}
(async () => {
  const lang = process.argv[2] || 'en'; const which = process.argv[3] || 'both';
  if (which !== 'alp') await nfe(lang);
  if (which !== 'nfe') await alp(lang);
})();
