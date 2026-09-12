import axios from 'axios';

// Centralized environment-based API base URL
// Development: http://127.0.0.1:8000
// Production: https://<deployed-cloud-run-url>
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

// Attach Authorization token to outgoing requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token') || localStorage.getItem('dolr_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Validate Content-Type and reject raw HTML responses
api.interceptors.response.use(
  (response) => {
    const contentType = response.headers?.['content-type'] || '';
    const isHtml = 
      contentType.includes('text/html') || 
      (typeof response.data === 'string' && response.data.trim().toLowerCase().startsWith('<!doctype html'));

    if (isHtml) {
      console.error('API endpoint returned HTML index page instead of JSON:', response.config?.url);
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
      console.error('API error response returned HTML index page:', error.config?.url);
      return Promise.reject(
        new Error('Backend API is unreachable or incorrectly routed. Please check backend deployment.')
      );
    }
    return Promise.reject(error);
  }
);

export default api;
