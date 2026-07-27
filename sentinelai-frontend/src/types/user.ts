export interface User {
  id: string;
  email: string;
  fullName: string;
  role: 'admin' | 'analyst' | 'viewer';
  isActive: boolean;
  isMfaEnabled: boolean;
  lastLogin: string | null;
  createdAt: string;
  avatar: string | null;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
  mfaCode?: string;
}

export interface UserPreferences {
  theme: 'dark' | 'light';
  sidebarCollapsed: boolean;
  notificationsEnabled: boolean;
  refreshInterval: number;
  defaultPageSize: number;
}
