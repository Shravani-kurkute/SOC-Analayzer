import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { authService } from '@services/authService';
import type { FrontendUser } from '@services/authService';

interface AuthState {
  isAuthenticated: boolean;
  user: FrontendUser | null;
  isLoading: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    isLoading: true,
  });

  useEffect(() => {
    const token = localStorage.getItem('sentinelai_auth_token');
    if (!token) {
      setState({ isAuthenticated: false, user: null, isLoading: false });
      return;
    }
    authService
      .getProfile()
      .then((user) => {
        setState({ isAuthenticated: true, user, isLoading: false });
      })
      .catch(() => {
        localStorage.removeItem('sentinelai_auth_token');
        localStorage.removeItem('sentinelai_refresh_token');
        setState({ isAuthenticated: false, user: null, isLoading: false });
      });
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { tokens, user } = await authService.login({ email, password });
    localStorage.setItem('sentinelai_auth_token', tokens.accessToken);
    localStorage.setItem('sentinelai_refresh_token', tokens.refreshToken);
    setState({ isAuthenticated: true, user, isLoading: false });
  }, []);

  const logout = useCallback(async () => {
    const rt = localStorage.getItem('sentinelai_refresh_token');
    try {
      if (rt) {
        await authService.logout(rt);
      }
    } finally {
      localStorage.removeItem('sentinelai_auth_token');
      localStorage.removeItem('sentinelai_refresh_token');
      setState({ isAuthenticated: false, user: null, isLoading: false });
    }
  }, []);

  const refreshToken = useCallback(async () => {
    const rt = localStorage.getItem('sentinelai_refresh_token');
    if (!rt) throw new Error('No refresh token');
    const tokens = await authService.refreshToken(rt);
    localStorage.setItem('sentinelai_auth_token', tokens.accessToken);
    localStorage.setItem('sentinelai_refresh_token', tokens.refreshToken);
  }, []);

  const value = useMemo(
    () => ({ ...state, login, logout, refreshToken }),
    [state, login, logout, refreshToken],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
