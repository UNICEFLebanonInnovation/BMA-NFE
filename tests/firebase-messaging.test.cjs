const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

// Replace CDN imports with mocked SDK bindings; execute the actual browser code.
const source = readFileSync(resolve(__dirname,
  '../student_registration/static/js/firebase-messaging.js'), 'utf8')
  .replace(/^import .*;\r?\n/gm, '');

async function run(options = {}) {
  const calls = { warnings: [], saved: [], tokens: 0, workers: 0, listeners: 0 };
  const notification = {
    permission: options.permission || 'granted',
    requestPermission: async () => {
      if (options.permissionError) throw new Error('Permission failed');
      return options.permission || 'granted';
    },
  };
  const sandbox = {
    window: { isSecureContext: options.secure !== false, Notification: notification },
    Notification: notification,
    navigator: { serviceWorker: { register: async () => {
      calls.workers++;
      if (options.workerError) throw new Error('Worker failed');
      return {};
    } } },
    document: { cookie: options.noCsrf ? '' : 'csrftoken=test', querySelector: () => null },
    console: { warn: (...args) => calls.warnings.push(args) },
    isSupported: async () => {
      if (options.supportError) throw new Error('Support check failed');
      return options.supported !== false;
    },
    initializeApp: () => ({}),
    getMessaging: () => ({}),
    onMessage: () => calls.listeners++,
    getToken: async () => {
      calls.tokens++;
      if (options.tokenError) throw new Error('messaging/token-subscribe-failed');
      return options.emptyToken ? '' : 'push-token';
    },
    fetch: async (url, request) => {
      calls.saved.push({ url, request });
      if (options.networkError) throw new Error('Network unavailable');
      return { ok: !options.saveError, status: options.saveError ? 403 : 200 };
    },
  };
  if (options.noNotifications) delete sandbox.window.Notification;
  if (options.noServiceWorker) delete sandbox.navigator.serviceWorker;
  // Await initialization so any escaped rejection fails the test.
  await vm.runInNewContext(source, sandbox);
  return calls;
}

test('saves a valid token with CSRF and same-origin credentials', async () => {
  const calls = await run();
  assert.equal(calls.listeners, 1);
  assert.equal(calls.saved.length, 1);
  assert.equal(calls.saved[0].url, '/api/save-fcm-token/');
  assert.equal(calls.saved[0].request.headers['X-CSRFToken'], 'test');
  assert.equal(calls.saved[0].request.credentials, 'same-origin');
  assert.deepEqual(JSON.parse(calls.saved[0].request.body), { token: 'push-token' });
  assert.equal(calls.warnings.length, 0);
});

for (const options of [
  { secure: false }, { supported: false }, { noNotifications: true },
  { noServiceWorker: true }, { permission: 'denied' }, { permission: 'default' },
]) {
  test(`skips unavailable notifications: ${JSON.stringify(options)}`, async () => {
    const calls = await run(options);
    assert.equal(calls.tokens, 0);
    assert.equal(calls.saved.length, 0);
    assert.equal(calls.warnings.length, 0);
  });
}

for (const failure of ['tokenError', 'workerError', 'permissionError', 'supportError', 'networkError', 'saveError']) {
  test(`handles ${failure} without an unhandled rejection`, async () => {
    const calls = await run({ [failure]: true });
    assert.equal(calls.warnings.length, 1);
    assert.match(calls.warnings[0][0], /Recent Exports/);
    if (failure === 'tokenError') {
      assert.equal(calls.listeners, 1);
      assert.equal(calls.saved.length, 0);
    }
  });
}

test('does not save an empty token or send a request without CSRF', async () => {
  assert.equal((await run({ emptyToken: true })).saved.length, 0);
  assert.equal((await run({ noCsrf: true })).saved.length, 0);
});
