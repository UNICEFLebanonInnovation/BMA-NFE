const fs = require('fs');
const path = require('path');
const NM = path.join(__dirname, '..', 'vendor', 'node_modules');
const MIME = { '.js': 'application/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.png': 'image/png', '.svg': 'image/svg+xml', '.map': 'application/json' };
function resolve(url) {
  const u = new URL(url);
  const p = u.pathname;
  let m;
  if (u.hostname === 'cdn.jsdelivr.net' && (m = p.match(/^\/npm\/(@?[^@\/]+(?:\/[^@\/]+)?)@[^\/]+(\/.*)?$/))) {
    let pkg = m[1], rest = m[2] || '';
    if (pkg === 'd3' && !rest) rest = '/dist/d3.min.js';
    return path.join(NM, pkg, rest);
  }
  if (u.hostname === 'cdnjs.cloudflare.com') {
    if ((m = p.match(/\/d3\/[^\/]+\/d3\.min\.js$/))) return path.join(NM, 'd3/dist/d3.min.js');
    if ((m = p.match(/\/font-awesome\/[^\/]+\/(.*)$/))) return path.join(NM, '@fortawesome/fontawesome-free', m[1]);
  }
  if (u.hostname === 'code.highcharts.com') return path.join(NM, 'highcharts', p);
  if (u.hostname === 'code.jquery.com') {
    if ((m = p.match(/^\/jquery-[\d.]+\.min\.js$/))) return path.join(NM, 'jquery/dist/jquery.min.js');
    if ((m = p.match(/^\/ui\/[\d.]+\/(.*)$/))) return path.join(NM, 'jquery-ui/dist', m[1]);
  }
  if (u.hostname === 'd3js.org') return path.join(NM, 'd3/dist/d3.min.js');
  if (u.hostname === 'unpkg.com' && (m = p.match(/^\/(@?[^@\/]+)@[^\/]+(\/.*)?$/))) return path.join(NM, m[1], m[2] || '');
  return null;
}
async function install(context) {
  await context.route(/^https?:\/\/(?!127\.0\.0\.1|localhost)/, async (route) => {
    const url = route.request().url();
    const file = resolve(url);
    if (file && fs.existsSync(file) && fs.statSync(file).isFile()) {
      return route.fulfill({ status: 200, contentType: MIME[path.extname(file)] || 'application/octet-stream', body: fs.readFileSync(file) });
    }
    if (!/googletagmanager|openstreetmap|tile\./.test(url)) console.log('UNRESOLVED', url);
    return route.abort();
  });
}
module.exports = { install };
