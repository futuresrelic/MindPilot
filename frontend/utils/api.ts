/**
 * API client for MindPilot backend
 */
import axios from 'axios';
import { useAuthStore } from '../state/authStore';

// Configure your API base URL
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  signup: (email: string, password: string, age_range?: string, goals?: string[]) =>
    api.post('/auth/signup', { email, password, age_range, goals }),

  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  getMe: () => api.get('/auth/me'),

  updateProfile: (data: { age_range?: string; goals?: string[]; theme?: string }) =>
    api.patch('/auth/me', data)
};

// Mood API
export const moodAPI = {
  checkIn: (mood_value: number, tags?: string[], note?: string) =>
    api.post('/mood/checkin', { mood_value, tags, note }),

  getHistory: (days = 30) =>
    api.get('/mood/history', { params: { days } }),

  getPatterns: (days = 30) =>
    api.get('/mood/patterns', { params: { days } }),

  getToday: () => api.get('/mood/today')
};

// Journal API
export const journalAPI = {
  createEntry: (text: string) =>
    api.post('/journal/entries', { text }),

  getEntries: (limit = 20, offset = 0) =>
    api.get('/journal/entries', { params: { limit, offset } }),

  getEntry: (id: number) =>
    api.get(`/journal/entries/${id}`),

  getWeeklySummary: () =>
    api.get('/journal/weekly-summary'),

  getInsights: (days = 30) =>
    api.get('/journal/insights', { params: { days } })
};

// Habits API
export const habitsAPI = {
  create: (data: { title: string; description?: string; recurrence?: string; reminders?: any[] }) =>
    api.post('/habits/', data),

  getAll: (include_inactive = false) =>
    api.get('/habits/', { params: { include_inactive } }),

  getOne: (id: number) =>
    api.get(`/habits/${id}`),

  update: (id: number, data: any) =>
    api.patch(`/habits/${id}`, data),

  complete: (id: number) =>
    api.post(`/habits/${id}/complete`),

  uncomplete: (id: number) =>
    api.delete(`/habits/${id}/complete`),

  delete: (id: number) =>
    api.delete(`/habits/${id}`)
};

// Sleep API
export const sleepAPI = {
  log: (data: { hours: number; quality?: number; notes?: string; bedtime?: string; waketime?: string }) =>
    api.post('/sleep/log', data),

  getHistory: (days = 30) =>
    api.get('/sleep/history', { params: { days } }),

  getStats: (days = 30) =>
    api.get('/sleep/stats', { params: { days } })
};

// Insights API
export const insightsAPI = {
  getWeekly: () => api.get('/insights/weekly'),

  getHistory: (limit = 10) =>
    api.get('/insights/history', { params: { limit } }),

  getHabitSuggestion: () =>
    api.get('/insights/habit-suggestion'),

  getDashboard: () =>
    api.get('/insights/dashboard')
};

// Audio API
export const audioAPI = {
  getContent: (category?: string) =>
    api.get('/audio/content', { params: { category } }),

  getDetail: (id: number) =>
    api.get(`/audio/content/${id}`),

  createSession: (data: { audio_id: string; duration_seconds: number; completed: boolean }) =>
    api.post('/audio/sessions', data),

  getHistory: (limit = 20) =>
    api.get('/audio/sessions', { params: { limit } }),

  getCategories: () =>
    api.get('/audio/categories')
};

// Subscription API
export const subscriptionAPI = {
  createCheckout: (price_id: string, success_url: string, cancel_url: string) =>
    api.post('/subscription/create-checkout', { price_id, success_url, cancel_url }),

  getStatus: () =>
    api.get('/subscription/status'),

  cancel: () =>
    api.post('/subscription/cancel'),

  getPlans: () =>
    api.get('/subscription/plans')
};

export default api;
