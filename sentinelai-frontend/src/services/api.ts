import axios, { type AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import type { APIError } from '@typings/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = import.meta.env.VITE_API_PREFIX || '/api/v1';
const TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT) || 30000;

let isRefreshing = false;
let pendingRequests: Array<(token: string) => void> = [];

function getStoredToken(): string | null {
  try {
    return localStorage.getItem('sentinelai_auth_token');
  } catch {
    return null;
  }
}

function getStoredRefreshToken(): string | null {
  try {
    return localStorage.getItem('sentinelai_refresh_token');
  } catch {
    return null;
  }
}

function clearSession(): void {
  try {
    localStorage.removeItem('sentinelai_auth_token');
    localStorage.removeItem('sentinelai_refresh_token');
    localStorage.removeItem('sentinelai_user');
  } catch {
    // localStorage may not be available
  }
}

export const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${API_PREFIX}`,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getStoredToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<APIError>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (!originalRequest || error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    // Don't try to refresh if the failing request was itself a refresh or login
    const url = originalRequest.url || '';
    if (url.includes('/auth/refresh') || url.includes('/auth/login')) {
      clearSession();
      window.location.href = '/login';
      return Promise.reject(error);
    }

    const refreshToken = getStoredRefreshToken();
    if (!refreshToken) {
      clearSession();
      window.location.href = '/login';
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve) => {
        pendingRequests.push((token: string) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          resolve(api(originalRequest));
        });
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const response = await axios.post(`${API_BASE_URL}${API_PREFIX}/auth/refresh`, {
        refresh_token: refreshToken,
      });
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('sentinelai_auth_token', access_token);
      localStorage.setItem('sentinelai_refresh_token', refresh_token);

      isRefreshing = false;
      pendingRequests.forEach((cb) => cb(access_token));
      pendingRequests = [];

      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
      }
      return api(originalRequest);
    } catch {
      isRefreshing = false;
      pendingRequests = [];
      clearSession();
      window.location.href = '/login';
      return Promise.reject(error);
    }
  },
);

export default api;
