# Export downloads and Firebase messaging

Completed export jobs store their download link in `ExportHistory.file_url`.
The Recent Exports menu uses that field and displays a labelled Download button.
NFR list exports also poll `/mscc/export-status/<id>/`; neither path requires push
notification registration to succeed. Filtered list exports download directly as
XLSX or CSV; the full asynchronous export wraps its output in a ZIP.
Refresh the page to update the Recent Exports menu after a background job finishes.

The NFR list search includes Governorate, based on the registration center's
governorate. Filtered exports apply the same governorate constraint, including
the default, selected-round and no-round export paths.

Local regression check: `python tests/check_export_download.py`. This runs against
disposable SQLite tables and local files, checks list filtering, generates an
XLSX through the actual export task, resolves its URL through the actual download
view twice, and reopens the downloaded workbook to check its rows. It does not
verify a deployed server or Azure storage configuration.

## Deploy and verify

Deploy the updated `student_registration/templates/base.html` and
`student_registration/static/js/firebase-messaging.js`. Run the normal static-file
collection/deployment and restart the web application as required by the host.
Reload the page to load the updated JavaScript.

1. Start an NFR list export with Excel selected. Confirm the polling download works.
2. Refresh and open Recent Exports. A completed job with a saved URL must show Download.
3. Open an older completed job's Download link and verify Excel opens the XLSX
   (for a ZIP export, extract the XLSX first).
4. Repeat with notifications blocked. Export downloads should still work.

## Investigate `messaging/token-subscribe-failed`

The JavaScript now handles registration and token-saving failures, including
unsupported browsers and denied notification permissions. It logs a diagnostic
warning instead of leaving an uncaught promise rejection. This does not repair
credentials or settings in Google Cloud; those must be verified separately.

For the current `leb-bma` project:

1. Compare the web app configuration in Firebase Console > Project settings >
   General with `firebaseConfig` in `static/js/firebase-messaging.js` and the
   configuration in `static/firebase-messaging-sw.js`. The API key, project ID,
   sender ID and app ID must belong to the same web app/project.
2. Compare the public `vapidKey` with Cloud Messaging > Web Push certificates for
   that same project. Keep any private keys and service-account credentials on
   the server.
3. Verify the FCM Registration API (`fcmregistrations.googleapis.com`) is enabled
   in that project. Check the browser API key's application restrictions allow
   the deployed site and its API restrictions allow Firebase Installations and
   FCM Registration.
4. In browser Network tools inspect the failed registration request and the
   preceding Firebase Installations request. Record the HTTP status and response
   error without sharing tokens. These responses are needed to distinguish a
   project/key mismatch, blocked API, or installation-authentication problem;
   the reported error alone does not establish which setting is wrong.
5. After correcting the configuration, reload and verify registration succeeds
   and `/api/save-fcm-token/` returns success. Test foreground and background
   notifications as well as the independent export download.

References:
- https://firebase.google.com/docs/cloud-messaging/web/get-started
- https://firebase.google.com/docs/projects/api-keys
