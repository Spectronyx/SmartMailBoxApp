import axios from 'axios';
import { authService } from './auth';

// Use environment variable for API URL (defaults to localhost for development)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 60000, // Increased to 60s for AI processing
  headers: {
    'Content-Type': 'application/json',
  },
});


// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = authService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, logout user
      authService.logout();
    }
    console.error('API Error:', error.response || error.message);
    return Promise.reject(error);
  }
);

export const mailboxService = {
  getAll: () => api.get('/mailboxes/'),
  create: (data) => api.post('/mailboxes/', data),
  sync: (id) => api.post(`/mailboxes/${id}/sync_emails/`),
  delete: (id) => api.delete(`/mailboxes/${id}/`),
  getSyncSettings: () => api.get('/mailboxes/sync_settings/'),
  updateSyncSettings: (minutes) => api.post('/mailboxes/sync_settings/', { interval_minutes: minutes }),
  connectImap: (data) => api.post('/mailboxes/', {
    email_address: data.email,
    password: data.password,
    provider: 'IMAP',
    imap_server: data.email.endsWith('@gmail.com') ? 'imap.gmail.com' : 'imap.mail.yahoo.com',
    imap_port: 993,
    use_ssl: true
  }),
};

export const emailService = {
  getAll: (params) => api.get('/emails/', { params }),
  get: (id) => api.get(`/emails/${id}/`),
  classify: (id) => api.post(`/emails/${id}/classify/`),
  classifyAll: () => api.post('/emails/classify/'),
  summarize: (id) => api.post(`/emails/${id}/summarize/`),
  summarizeAll: () => api.post('/emails/summarize/'),
  extractTasks: () => api.post('/emails/extract-tasks/'),
  clearData: () => api.post('/emails/clear-data/'),
};

export const taskService = {
  getAll: (params) => api.get('/tasks/', { params }),
  update: (id, data) => api.patch(`/tasks/${id}/`, data),
  delete: (id) => api.delete(`/tasks/${id}/`),
  runReminders: () => api.post('/tasks/run-reminders/'),
  exportIcs: (id) => `${API_BASE_URL}/api/tasks/${id}/export-ics/`,
  exportCalendar: () => `${API_BASE_URL}/api/tasks/export-calendar/`,
};


export default api;