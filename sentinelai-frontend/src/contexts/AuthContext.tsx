import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { authService } from '@services/authService';
import type { User } from '@typings/user';

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  getAccessToken: () => string | null;
}

const TOKEN_KEY = 'sentinelai_auth_token';
const REFRESH_KEY = 'sentinelai_refresh_token';
const USER_KEY = 'sentinelai_user';

const AuthContext = createContext<AuthContextType | null>(null);

function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

function getStoredRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY);
}

function getStoredUser(): User | null {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function storeSession(accessToken: string, refreshToken: string, user: User): void {
  localStorage.setItem(TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_KEY, refreshToken);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
}

function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split('.');
    const payloadStr = parts[1];
    if (parts.length !== 3 || !payloadStr) return true;
    const payload = JSON.parse(atob(payloadStr));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const token = getStoredToken();
    const user = getStoredUser();
    if (token && !isTokenExpired(token)) {
      if (user) {
        return { isAuthenticated: true, user, isLoading: false };
      }
      return { isAuthenticated: false, user: null, isLoading: true };
    }
    if (token && isTokenExpired(token)) {
      const refresh = getStoredRefreshToken();
      if (refresh) {
        return { isAuthenticated: false, user: null, isLoading: true };
      }
    }
    clearSession();
    return { isAuthenticated: false, user: null, isLoading: false };
  });

  const refreshAccessToken = useCallback(async (): Promise<boolean> => {
    const refreshToken = getStoredRefreshToken();
    if (!refreshToken) return false;
    try {
      const res = await authService.refreshToken(refreshToken);
      localStorage.setItem(TOKEN_KEY, res.access_token);
      localStorage.setItem(REFRESH_KEY, res.refresh_token);
      return true;
    } catch {
      clearSession();
      setState({ isAuthenticated: false, user: null, isLoading: false });
      return false;
    }
  }, []);

  useEffect(() => {
    if (state.isLoading) {
      refreshAccessToken().then((ok) => {
        if (ok) {
          const user = getStoredUser();
          if (user) {
            setState({ isAuthenticated: true, user, isLoading: false });
          } else {
            tryFetchProfile();
          }
        }
      });
    }
  }, []);

  const tryFetchProfile = useCallback(async () => {
    try {
      const user = await authService.getProfile();
      const token = getStoredToken();
      const refresh = getStoredRefreshToken();
      if (token && refresh) {
        storeSession(token, refresh, user);
      }
      setState({ isAuthenticated: true, user, isLoading: false });
    } catch {
      clearSession();
      setState({ isAuthenticated: false, user: null, isLoading: false });
    }
  }, []);

  const login = useCallback(async (email: string, password: string): Promise<void> => {
    setState((prev) => ({ ...prev, isLoading: true }));
    try {
      const res = await authService.login({ email, password });
      storeSession(res.access_token, res.refresh_token, res.user);
      setState({ isAuthenticated: true, user: res.user, isLoading: false });
    } catch (err: unknown) {
      clearSession();
      setState({ isAuthenticated: false, user: null, isLoading: false });
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response: { data: { message?: string } } }).response?.data?.message || 'Login failed'
          : 'Login failed';
      throw new Error(message);
    }
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    const refreshToken = getStoredRefreshToken();
    if (refreshToken) {
      try {
        await authService.logout(refreshToken);
      } catch {
        // even if server logout fails, clear local session
      }
    }
    clearSession();
    setState({ isAuthenticated: false, user: null, isLoading: false });
  }, []);

  const getAccessToken = useCallback((): string | null => {
    return getStoredToken();
  }, []);

  const value = useMemo(
    () => ({ ...state, login, logout, getAccessToken }),
    [state, login, logout, getAccessToken],
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
