importScripts("https://www.gstatic.com/firebasejs/12.0.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/12.0.0/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyAL2iS7YCesCURrxFViKUzH8LOrDzDIPHg",
  authDomain: "leb-bma.firebaseapp.com",
  projectId: "leb-bma",
  storageBucket: "leb-bma.firebasestorage.app",
  messagingSenderId: "455115377412",
  appId: "1:455115377412:web:1e39a332cd97f98e009e51",
  measurementId: "G-1QPVEZK990",
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function (payload) {
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/static/images/logo.png',
  };
  self.registration.showNotification(notificationTitle, notificationOptions);
});
