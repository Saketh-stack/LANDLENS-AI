import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import axios from 'axios'
import './index.css'
import App from './App.jsx'
import { ErrorBoundary } from './components/ErrorBoundary.jsx'

if (import.meta.env.VITE_API_URL) {
  axios.defaults.baseURL = import.meta.env.VITE_API_URL
}

// Intercept HTML responses from SPA rewrites when calling API routes
axios.interceptors.response.use(
  (response) => {
    if (typeof response.data === 'string' && response.data.trim().toLowerCase().startsWith('<!doctype html')) {
      return Promise.reject(new Error('API endpoint returned HTML index page. Backend service is offline or not routed.'));
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
