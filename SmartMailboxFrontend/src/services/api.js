import axios from 'axios';
import { authService } from './auth';

// Create axios instance with default config
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
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
};

export default api;