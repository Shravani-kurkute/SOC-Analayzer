import api from './api';
import type { APIResponse } from '@typings/api';
import type { AuthTokens, LoginCredentials, User } from '@typings/user';

export const authService = {
  async login(credentials: LoginCredentials): Promise<APIResponse<AuthTokens>> {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } finally {
      localStorage.removeItem('sentinelai_auth_token');
      localStorage.removeItem('sentinelai_refresh_token');
    }
  },

  async refreshToken(refreshToken: string): Promise<APIResponse<AuthTokens>> {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },

  async getProfile(): Promise<APIResponse<User>> {
    const response = await api.get('/auth/profile');
    return response.data;
  },

  async updateProfile(data: Partial<User>): Promise<APIResponse<User>> {
    const response = await api.patch('/auth/profile', data);
    return response.data;
  },

  async forgotPassword(email: string): Promise<APIResponse<null>> {
    const response = await api.post('/auth/forgot-password', { email });
    return response.data;
  },

  async resetPassword(token: string, password: string): Promise<APIResponse<null>> {
    const response = await api.post('/auth/reset-password', { token, password });
    return response.data;
  },

  async setupMfa(): Promise<APIResponse<{ secret: string; qrCode: string }>> {
    const response = await api.post('/auth/mfa/setup');
    return response.data;
  },

  async verifyMfa(code: string): Promise<APIResponse<null>> {
    const response = await api.post('/auth/mfa/verify', { code });
    return response.data;
  },
};
