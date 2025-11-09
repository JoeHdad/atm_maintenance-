import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

console.log('[index.js] Starting application...');

// Global error handler for unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  console.error('[Global] Unhandled promise rejection:', event.reason);
  // Prevent the default browser behavior
  event.preventDefault();
});

// Global error handler for runtime errors
window.addEventListener('error', (event) => {
  console.error('[Global] Runtime error caught:', event.error);
  // Don't prevent default - let ErrorBoundary handle it
});

console.log('[index.js] Creating React root...');
const root = ReactDOM.createRoot(document.getElementById('root'));

console.log('[index.js] Rendering App...');
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

console.log('[index.js] App rendered');

// Register Service Worker for PWA functionality (production only)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    if (process.env.NODE_ENV === 'production') {
      navigator.serviceWorker
        .register('/service-worker.js')
        .then((registration) => {
          console.log('Service Worker registered successfully:', registration.scope);
        })
        .catch((error) => {
          console.log('Service Worker registration failed:', error);
        });
    } else {
      // Ensure any previously registered service workers are cleared in development
      navigator.serviceWorker.getRegistrations().then((registrations) => {
        registrations.forEach((registration) => {
          console.log('[ServiceWorker] Unregistering dev service worker:', registration.scope);
          registration.unregister();
        });
      })
      .catch((error) => {
        console.log('[ServiceWorker] Failed to unregister dev service workers:', error);
      });
    }
  });
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
