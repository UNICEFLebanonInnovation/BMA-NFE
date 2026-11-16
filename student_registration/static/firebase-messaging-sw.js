importScripts("https://www.gstatic.com/firebasejs/12.0.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/12.0.0/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyCfHk4d_bUgJcU-KI4wve7ZuA4YDlCHYVg",
  authDomain: "bma-nfe.firebaseapp.com",
  projectId: "bma-nfe",
  storageBucket: "bma-nfe.firebasestorage.app",
  messagingSenderId: "427743071075",
  appId: "1:427743071075:web:c089e6f26c16c0142fe156",
  measurementId: "G-XCEDM17QFX"
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
