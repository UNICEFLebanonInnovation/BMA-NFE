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
  const calls = { warnings: [], saved: [], tokens: 0, workers: 0, listeners: 0, unsubscribes: 0 };
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
      return { pushManager: { getSubscription: async () => {
        if (!options.pushKey) return null;
        const publicKey = options.pushKey === 'current'
          ? 'BLJ6-9NoQ9xhZ7KFBiU5ijOargaiaOn6LJ_JwjtY4A4W04XnThpJVpW8nNtQmc7wFNkd2lvVQUyU5tiqNTOpRZA'
          : 'BAwRHhzYusFpd-Z_CTfU3AE1w_LuOgCJ2LpTQMPbIUNZQv343yQwd2fF49XxGj09AwArLcZ7icVMTlgxcaX53nE';
        return {
          options: { applicationServerKey: Uint8Array.from(Buffer.from(publicKey, 'base64url')).buffer },
          unsubscribe: async () => { calls.unsubscribes++; return !options.unsubscribeError; },
        };
      } } };
    } } },
    document: { cookie: options.noCsrf ? '' : 'csrftoken=test', querySelector: () => null },
    console: { warn: (...args) => calls.warnings.push(args) },
    btoa,
    isSupported: async () => {
      if (options.supportError) throw new Error('Support check failed');
      return options.supported !== false;
    },
    initializeApp: (config) => { calls.config = config; return {}; },
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


test('page and service worker use the same bma-nfe Firebase configuration', async () => {
  const page = await run();
  let workerConfig;
  const workerSource = readFileSync(resolve(__dirname,
    '../student_registration/static/firebase-messaging-sw.js'), 'utf8');
  vm.runInNewContext(workerSource, {
    importScripts: () => {},
    firebase: {
      initializeApp: (config) => { workerConfig = config; },
      messaging: () => ({ onBackgroundMessage: () => {} }),
    },
  });
  assert.equal(workerConfig.projectId, 'bma-nfe');
  assert.deepEqual(JSON.parse(JSON.stringify(workerConfig)),
    JSON.parse(JSON.stringify(page.config)));
});


test('replaces a subscription made with the previous VAPID key before saving a new token', async () => {
  const calls = await run({ pushKey: 'previous' });
  assert.equal(calls.unsubscribes, 1);
  assert.equal(calls.saved.length, 1);
  assert.equal(calls.warnings.length, 0);
});

test('keeps a subscription that already uses the current VAPID key', async () => {
  const calls = await run({ pushKey: 'current' });
  assert.equal(calls.unsubscribes, 0);
  assert.equal(calls.saved.length, 1);
});

test('does not register a token if refreshing the old subscription fails', async () => {
  const calls = await run({ pushKey: 'previous', unsubscribeError: true });
  assert.equal(calls.tokens, 0);
  assert.equal(calls.saved.length, 0);
  assert.equal(calls.warnings.length, 1);
});
