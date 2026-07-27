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
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('sentinelai_refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}${API_PREFIX}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token } = response.data.data;
          localStorage.setItem('sentinelai_auth_token', access_token);
          if (error.config) {
            error.config.headers.Authorization = `Bearer ${access_token}`;
            return api(error.config);
          }
        } catch {
          localStorage.removeItem('sentinelai_auth_token');
          localStorage.removeItem('sentinelai_refresh_token');
          window.location.href = '/login';
        }
      } else {
        localStorage.removeItem('sentinelai_auth_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);

export default api;
