import { initializeApp } from "https://www.gstatic.com/firebasejs/12.0.0/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/12.0.0/firebase-messaging.js";

const firebaseConfig = {
  apiKey: "AIzaSyAL2iS7YCesCURrxFViKUzH8LOrDzDIPHg",
  authDomain: "leb-bma.firebaseapp.com",
  projectId: "leb-bma",
  storageBucket: "leb-bma.firebasestorage.app",
  messagingSenderId: "455115377412",
  appId: "1:455115377412:web:1e39a332cd97f98e009e51",
  measurementId: "G-1QPVEZK990",
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);
window.firebaseMessaging = messaging;


navigator.serviceWorker
  .register("/static/firebase-messaging-sw.js")
  .then((registration) => {
    Notification.requestPermission().then((permission) => {
      if (permission === "granted") {
        getToken(messaging, {
          vapidKey: "BAwRHhzYusFpd-Z_CTfU3AE1w_LuOgCJ2LpTQMPbIUNZQv343yQwd2fF49XxGj09AwArLcZ7icVMTlgxcaX53nE",
          serviceWorkerRegistration: registration,
        }).then((token) => {
          const csrfToken = document.cookie
            .split("; ")
            .find((row) => row.startsWith("csrftoken="))
            ?.split("=")[1];

          fetch("/api/save-fcm-token/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ token }),
          });
        });
      }
    });
  });

onMessage(messaging, (payload) => {
  if (payload.data && (payload.data.type === "mscc_export_ready" || payload.data.type === "mscc_export_failed" || payload.data.type === "advanced_export_ready" || payload.data.type === "advanced_export_failed")) {
    const isSuccess = payload.data.type === "mscc_export_ready" || payload.data.type === "advanced_export_ready";

    if (!document.hidden) {
        if (isSuccess) {
            $('#downloadReadyModal .download-link').attr('href', payload.data.url);
            const downloadModal = new bootstrap.Modal(document.getElementById('downloadReadyModal'));
            downloadModal.show();

            // Reload on close to update the notification list
            document.getElementById('downloadReadyModal').addEventListener('hidden.bs.modal', function () {
                if (window.location.pathname.includes('/mscc/list/') || window.location.pathname.includes('/mscc/dashboard/')) {
                    window.location.reload();
                }
            }, { once: true });
        } else {
            const reason = payload.data.reason || 'Unknown error';
            alert('Export failed: ' + reason);
            if (window.location.pathname.includes('/mscc/list/') || window.location.pathname.includes('/mscc/dashboard/')) {
                window.location.reload();
            }
        }
    } else {
        // If document is hidden, just reload if needed when user comes back, or trust push notification
        // For simplicity, we can reload next time they are on the page, but here we just check if we should have reloaded
        if (window.location.pathname.includes('/mscc/list/') || window.location.pathname.includes('/mscc/dashboard/')) {
             // We can't really reload if hidden effectively for the user, but it's okay.
        }
    }
  }
});
