const { start } = require('./lib');
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
async function step(name, fn) { if (process.env.ONLY && !process.env.ONLY.split(',').includes(name)) return; try { await fn(); } catch (e) { console.log('ERR[' + name + ']', e.message.split('\n').slice(0, 3).join(' / ')); } }
async function wait(page, ms = 700) { await page.waitForLoadState('networkidle'); await sleep(ms); }
(async () => {
  const lang = process.argv[2] || 'en';
  const s = await start(lang); const { page } = s;
  const NEWUSER = 'center.metn';
  const nosb = lang === 'ar';
  const shot = (n, o = {}) => s.shot(n, Object.assign({}, o, nosb ? { nosidebar: true } : {}));
  const tab = async (i) => { await page.locator('form .nav-tabs .nav-link').nth(i).click(); await sleep(500); };
  await step('login', async () => {
    await s.goto('/accounts/login/'); await s.setLang(lang);
    await s.goto('/admin/login/?next=/admin/', 800); await shot('adm_00_login_empty');
    await page.fill('input[name="username"]', 'admin'); await page.fill('input[name="password"]', 'Admin@Demo2026!'); await shot('adm_00_login_filled');
    await page.click('form button[type="submit"]'); await wait(page, 1200); await s.setLang(lang); await s.goto('/admin/', 1200);
    await shot('adm_01_dashboard'); await shot('adm_01_dashboard_full', { full: true });
    await page.locator('.navbar-nav .nav-link[data-toggle="dropdown"], .navbar .dropdown-toggle').last().click(); await sleep(500); await shot('adm_02_user_menu'); await page.keyboard.press('Escape');
  });
  await step('users_list', async () => {
    await s.goto('/admin/users/user/', 1000); await shot('adm_10_users_list');
    await page.fill('input[name="q"]', 'rania'); await page.keyboard.press('Enter'); await wait(page, 800); await shot('adm_11_users_search');
    await s.goto('/admin/users/user/?groups__id__exact=' + (await page.evaluate(() => { const o = Array.from(document.querySelectorAll('select option')).find(o => o.textContent.trim() === 'MSCC_CENTER'); return o ? o.value : '2'; })), 1000); await shot('adm_12_users_filtered');
    await s.goto('/admin/users/user/export/', 800); await shot('adm_14_users_export', { full: true, nosidebar: true });
    await s.goto('/admin/users/user/import/', 800); await shot('adm_15_users_import', { full: true, nosidebar: true });
  });
  let newId = null;
  await step('add_user', async () => {
    await s.goto('/admin/users/user/add/', 800); await shot('adm_20_add_user_empty', { full: true, nosidebar: true });
    await page.fill('input[name="username"]', NEWUSER); await page.fill('input[name="password1"]', 'Metn@Demo2026!'); await page.fill('input[name="password2"]', 'Metn@Demo2026!');
    await shot('adm_21_add_user_filled', { full: true, nosidebar: true });
    await page.click('input[name="_save"], button[name="_save"]'); await wait(page, 1000); await shot('adm_22_add_user_saved', { full: true, nosidebar: true });
    const m = page.url().match(/user\/(\d+)\/change/); if (m) newId = m[1];
    await tab(1);
    await page.fill('#id_first_name', 'Samar'); await page.fill('#id_last_name', 'Chehab'); await page.fill('#id_email', 'samar@example.org');
    await page.selectOption('#id_partner', '1'); await page.fill('#id_phone_number', '03-222333'); await page.selectOption('#id_center', '2');
    await shot('adm_23_add_user_personal_info', { full: true, nosidebar: true });
    await tab(2);
    for (const n of ['MSCC', 'MSCC_CENTER']) { await page.locator('#id_groups_from option').filter({ hasText: new RegExp('^' + n + '$') }).dblclick(); await sleep(300); }
    await shot('adm_24_add_user_permissions', { full: true, nosidebar: true });
    await page.click('input[name="_save"], button[name="_save"]'); await wait(page, 1000); await shot('adm_25_add_user_done');
  });
  if (!newId) { await s.goto('/admin/users/user/?q=' + NEWUSER); const href = await page.locator('table a[href*="/change/"]').first().getAttribute('href'); newId = href.match(/user\/(\d+)\//)[1]; }
  await step('alp_user', async () => {
    await s.goto('/admin/users/user/?q=alp.school', 800); const href = await page.locator('table a[href*="/change/"]').first().getAttribute('href'); await s.goto(href, 1000);
    await tab(1); await shot('adm_30_alp_user_personal_info', { full: true, nosidebar: true });
    try { const sel = page.locator('.field-school .select2-selection, #div_id_school .select2-selection, [class*="school"] .select2-selection').first(); await sel.scrollIntoViewIfNeeded(); await page.evaluate(() => window.scrollBy(0, -250)); await sleep(300); await sel.click({ timeout: 4000 }); await sleep(400); await page.keyboard.type('Beirut'); await sleep(1500); await shot('adm_32_school_autocomplete'); await page.keyboard.press('Escape'); } catch (e) { console.log('autocomplete skipped', e.message.split('\n')[0]); }
    await tab(2); await shot('adm_31_alp_user_permissions', { full: true, nosidebar: true });
    await s.goto(new URL(page.url()).pathname.replace(/change\/?$/, 'history/'), 800); await shot('adm_62_user_history', { full: true, nosidebar: true });
  });
  await step('reset_password', async () => {
    await s.goto(`/admin/users/user/${newId}/change/`, 800); await page.click('a[href$="/password/"]'); await wait(page, 800); await shot('adm_40_reset_password_empty', { full: true, nosidebar: true });
    await page.fill('input[name="password1"]', 'Metn@New2026!'); await page.fill('input[name="password2"]', 'Metn@New2026!'); await shot('adm_41_reset_password_filled', { full: true, nosidebar: true });
    await page.press('input[name="password2"]', 'Enter'); await wait(page, 1000); await shot('adm_42_reset_password_done');
  });
  await step('deactivate', async () => {
    await s.goto('/admin/users/user/', 800); await page.evaluate((id) => { const cb = document.querySelector('input[name="_selected_action"][value="' + id + '"]'); cb.checked = true; cb.dispatchEvent(new Event('change', { bubbles: true })); }, String(newId)); await page.selectOption('select[name="action"]', 'disable'); await sleep(300); await shot('adm_50_action_disable');
    await page.click('button[name="index"], button[title="Run the selected action"], .actions button[type="submit"]'); await wait(page, 1000); await shot('adm_51_user_disabled');
    await page.evaluate((id) => { const cb = document.querySelector('input[name="_selected_action"][value="' + id + '"]'); cb.checked = true; cb.dispatchEvent(new Event('change', { bubbles: true })); }, String(newId)); await page.selectOption('select[name="action"]', 'activate'); await page.click('button[name="index"], .actions button[type="submit"]'); await wait(page, 800);
    await s.goto(`/admin/users/user/${newId}/delete/`, 800); await shot('adm_52_delete_user_confirm', { full: true, nosidebar: true });
  });
  await step('groups', async () => {
    await s.goto('/admin/auth/group/', 800); await shot('adm_60_groups_list'); await shot('adm_60_groups_list_full', { full: true });
    await s.goto('/admin/auth/group/1/change/', 800); await shot('adm_61_group_change', { full: true, nosidebar: true });
  });
  await step('reference', async () => {
    for (const [n, u] of [['adm_70_partners', '/admin/schools/partnerorganization/'], ['adm_71_partner_change', '/admin/schools/partnerorganization/1/change/'], ['adm_72_centers', '/admin/locations/center/'], ['adm_73_center_change', '/admin/locations/center/1/change/'], ['adm_74_schools', '/admin/schools/school/'], ['adm_75_school_change', '/admin/schools/school/1/change/'], ['adm_76_rounds', '/admin/mscc/round/'], ['adm_77_round_change', '/admin/mscc/round/2/change/'], ['adm_78_alp_rounds', '/admin/alp/alpround/'], ['adm_79_alp_programs', '/admin/alp/alpprogram/'], ['adm_80_alp_grading_definitions', '/admin/alp/alpgradingdefinition/'], ['adm_81_packages', '/admin/mscc/packages/'], ['adm_82_nationalities', '/admin/students/nationality/'], ['adm_83_locations', '/admin/locations/location/'], ['adm_84_educational_levels', '/admin/schools/educationallevel/']]) {
      await step(n, async () => { await s.goto(u, 900); await shot(n, /_change$/.test(n) ? { full: true, nosidebar: true } : {}); });
    }
  });
  await step('monitoring', async () => {
    for (const [n, u] of [['adm_90_user_activity', '/admin/backends/useractivity/'], ['adm_91_export_history', '/admin/backends/exporthistory/'], ['adm_92_task_logs', '/admin/taskapp/taskrunlog/'], ['adm_93_registrations', '/admin/mscc/registration/'], ['adm_94_children', '/admin/child/child/']]) {
      await step(n, async () => { await s.goto(u, 900); await shot(n); });
    }
  });
  await s.close();
})();
