import api from './api';
import type { AuthTokens, LoginCredentials } from '@typings/user';

interface BackendUser {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'manager' | 'analyst' | 'viewer';
  is_active: boolean;
  mfa_enabled: boolean;
  last_login: string | null;
  created_at: string;
  updated_at: string;
}

interface BackendAuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: BackendUser;
}

interface BackendTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface FrontendUser {
  id: string;
  email: string;
  fullName: string;
  role: 'admin' | 'analyst' | 'viewer';
  isActive: boolean;
}

function mapUser(bu: BackendUser): FrontendUser {
  return {
    id: bu.id,
    email: bu.email,
    fullName: bu.full_name,
    role: bu.role === 'manager' ? 'admin' : (bu.role as 'admin' | 'analyst' | 'viewer'),
    isActive: bu.is_active,
  };
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<{ tokens: AuthTokens; user: FrontendUser }> {
    const response = await api.post<BackendAuthResponse>('/auth/login', credentials);
    const data = response.data;
    return {
      tokens: {
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        expiresIn: data.expires_in,
      },
      user: mapUser(data.user),
    };
  },

  async logout(refreshToken: string): Promise<void> {
    try {
      await api.post('/auth/logout', { refresh_token: refreshToken });
    } finally {
      localStorage.removeItem('sentinelai_auth_token');
      localStorage.removeItem('sentinelai_refresh_token');
    }
  },

  async refreshToken(token: string): Promise<AuthTokens> {
    const response = await api.post<BackendTokenResponse>('/auth/refresh', { refresh_token: token });
    const data = response.data;
    return {
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
      expiresIn: data.expires_in,
    };
  },

  async getProfile(): Promise<FrontendUser> {
    const response = await api.get<BackendUser>('/auth/me');
    return mapUser(response.data);
  },
};
