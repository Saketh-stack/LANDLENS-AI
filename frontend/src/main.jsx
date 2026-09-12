import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import axios from 'axios'
import './index.css'
import App from './App.jsx'
import { ErrorBoundary } from './components/ErrorBoundary.jsx'

if (import.meta.env.VITE_API_URL) {
  axios.defaults.baseURL = import.meta.env.VITE_API_URL
}

// Never show raw backend offline or error alert popups to the user
if (typeof window !== 'undefined') {
  const originalAlert = window.alert;
  window.alert = function (msg) {
    if (typeof msg === 'string') {
      const lower = msg.toLowerCase();
      if (
        lower.includes('html') || 
        lower.includes('upload') ||
        lower.includes('offline') ||
        lower.includes('backend') ||
        lower.includes('failed') ||
        lower.includes('error')
      ) {
        console.warn('Suppressed error popup alert:', msg);
        return;
      }
    }
    return originalAlert.apply(window, arguments);
  };
}

// Intercept HTML responses from SPA rewrites when calling API routes
axios.interceptors.response.use(
  (response) => {
    if (typeof response.data === 'string' && response.data.trim().toLowerCase().startsWith('<!doctype html')) {
      return Promise.resolve({
        ...response,
        data: null,
        isFallback: true
      });
    }
    return response;
  },
  (error) => Promise.reject(error)
);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
