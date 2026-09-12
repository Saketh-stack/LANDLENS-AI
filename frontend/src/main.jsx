import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import axios from 'axios'
import './index.css'
import App from './App.jsx'
import { ErrorBoundary } from './components/ErrorBoundary.jsx'

// Configure Centralized API Base URL
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '';
if (apiBaseUrl) {
  axios.defaults.baseURL = apiBaseUrl;
}

// Global Response Interceptor: Validate response Content-Type and strictly reject HTML index pages
axios.interceptors.response.use(
  (response) => {
    const contentType = response.headers?.['content-type'] || '';
    const isHtml = 
      contentType.includes('text/html') || 
      (typeof response.data === 'string' && response.data.trim().toLowerCase().startsWith('<!doctype html'));

    if (isHtml) {
      return Promise.reject(
        new Error('Backend API is unreachable or incorrectly routed. Please check backend deployment.')
      );
    }
    return response;
  },
  (error) => {
    const contentType = error.response?.headers?.['content-type'] || '';
    const isHtml = 
      contentType.includes('text/html') || 
      (typeof error.response?.data === 'string' && error.response.data.trim().toLowerCase().startsWith('<!doctype html'));

    if (isHtml) {
      return Promise.reject(
        new Error('Backend API is unreachable or incorrectly routed. Please check backend deployment.')
      );
    }
    return Promise.reject(error);
  }
);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
