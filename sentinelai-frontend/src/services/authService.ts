import api from './api';
import type { AuthResponse, LoginCredentials, TokenResponse, User } from '@typings/user';

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  async logout(refreshToken: string): Promise<void> {
    try {
      await api.post('/auth/logout', { refresh_token: refreshToken });
    } finally {
      localStorage.removeItem('sentinelai_auth_token');
      localStorage.removeItem('sentinelai_refresh_token');
      localStorage.removeItem('sentinelai_user');
    }
  },

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },

  async getProfile(): Promise<User> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async forgotPassword(email: string): Promise<void> {
    await api.post('/auth/forgot-password', { email });
  },

  async resetPassword(token: string, password: string): Promise<void> {
    await api.post('/auth/reset-password', { token, password });
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },
};
