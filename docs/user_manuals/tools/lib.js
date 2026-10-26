const { chromium } = require('playwright');
const cdn = require('./cdn');
const fs = require('fs');
const path = require('path');
const BASE = 'http://127.0.0.1:8000';
const OUT = process.env.SHOT_DIR || path.join(__dirname, '..', 'shots');

async function start(lang) {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1, locale: lang === 'ar' ? 'ar' : 'en-US' });
  await cdn.install(context);
  const page = await context.newPage();
  page.setDefaultTimeout(20000);
  const dir = path.join(OUT, lang);
  fs.mkdirSync(dir, { recursive: true });
  const api = {
    browser, context, page, lang, dir,
    url: (p) => BASE + p,
    async goto(p, wait = 500) { await page.goto(BASE + p, { waitUntil: 'networkidle' }); await page.waitForTimeout(wait); },
    async shot(name, opts = {}) {
      const file = path.join(dir, name + '.png');
      if (opts.el) { const el = typeof opts.el === 'string' ? page.locator(opts.el).first() : opts.el; await el.screenshot({ path: file }); }
      else if (opts.full || opts.nosidebar) {
        const css = (opts.full ? 'nav.sidebar.d-lg-block{position:static !important;} header.topbar{position:static !important;} #nfe_search_loader{display:none !important;}' : '')
          + (opts.nosidebar ? ' .main-sidebar{display:none !important;} .content-wrapper,.main-header,.main-footer{margin-left:0 !important;margin-right:0 !important;}' : '');
        const h = await page.addStyleTag({ content: css }); await page.waitForTimeout(150);
        await page.screenshot({ path: file, fullPage: !!opts.full }); await h.evaluate(e => e.remove());
      }
      else await page.screenshot({ path: file, clip: opts.clip });
      console.log('shot', lang, name);
      return file;
    },
    async login(user, pw) {
      await page.goto(BASE + '/accounts/login/', { waitUntil: 'networkidle' });
      await page.fill('input[name="login"]', user);
      await page.fill('input[name="password"]', pw);
      await page.click('button[type="submit"]');
      await page.waitForLoadState('networkidle');
    },
    async setLang(code) {
      const cookies = await context.cookies();
      const csrf = (cookies.find(c => c.name === 'csrftoken') || {}).value;
      await page.evaluate(async ({ code, csrf }) => {
        const fd = new URLSearchParams(); fd.append('language', code); fd.append('csrfmiddlewaretoken', csrf); fd.append('next', '/');
        await fetch('/i18n/setlang/', { method: 'POST', body: fd, headers: { 'X-CSRFToken': csrf }, redirect: 'manual' });
      }, { code, csrf });
    },
    async close() { await browser.close(); },
  };
  return api;
}
module.exports = { start, BASE };
