import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import type { ReactNode } from 'react';

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean;
}

interface User {
  id: string;
  email: string;
  fullName: string;
  role: 'admin' | 'analyst' | 'viewer';
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    isLoading: false,
  });

  const login = useCallback(async (_email: string, _password: string) => {
    // Will be implemented in Module 1
  }, []);

  const logout = useCallback(() => {
    setState({ isAuthenticated: false, user: null, isLoading: false });
  }, []);

  const refreshToken = useCallback(async () => {
    // Will be implemented in Module 1
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
