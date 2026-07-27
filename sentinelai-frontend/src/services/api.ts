import axios, { type AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import type { APIError } from '@typings/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = import.meta.env.VITE_API_PREFIX || '/api/v1';
const TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT) || 30000;

export const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${API_PREFIX}`,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;
let pendingQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null) {
  for (const item of pendingQueue) {
    if (error || !token) {
      item.reject(error);
    } else {
      item.resolve(token);
    }
  }
  pendingQueue = [];
}

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('sentinelai_auth_token');
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
    const originalRequest = error.config;
    if (!originalRequest || error.response?.status !== 401) {
      return Promise.reject(error);
    }

    if (originalRequest.url?.includes('/auth/refresh') || originalRequest.url?.includes('/auth/login')) {
      return Promise.reject(error);
    }

    const refreshToken = localStorage.getItem('sentinelai_refresh_token');
    if (!refreshToken) {
      localStorage.removeItem('sentinelai_auth_token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        pendingQueue.push({ resolve, reject });
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return api(originalRequest);
      });
    }

    isRefreshing = true;

    try {
      const response = await axios.post(`${API_BASE_URL}${API_PREFIX}/auth/refresh`, {
        refresh_token: refreshToken,
      });
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('sentinelai_auth_token', access_token);
      localStorage.setItem('sentinelai_refresh_token', refresh_token);
      processQueue(null, access_token);
      originalRequest.headers.Authorization = `Bearer ${access_token}`;
      return api(originalRequest);
    } catch (err) {
      processQueue(err, null);
      localStorage.removeItem('sentinelai_auth_token');
      localStorage.removeItem('sentinelai_refresh_token');
      window.location.href = '/login';
      return Promise.reject(err);
    } finally {
      isRefreshing = false;
    }
  },
);

export default api;
