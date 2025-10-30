import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/lib/api';
import { User } from '@/lib/types';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('auth_token');
    const storedRefreshToken = localStorage.getItem('refresh_token');

    if (token && storedRefreshToken) {
      apiClient.setToken(token);
      setRefreshToken(storedRefreshToken);
      apiClient
        .getMe()
        .then((userData) => setUser(userData))
        .catch(() => {
          localStorage.removeItem('auth_token');
          apiClient.setToken(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await apiClient.login(email, password);
    setUser(response.user);
    if (response.refresh_token) {
      setRefreshToken(response.refresh_token);
      localStorage.setItem('refresh_token', response.refresh_token);
    }
  };

  const register = async (email: string, password: string, name: string) => {
    // Note: The backend expects the password to be at least 8 characters long,
    // with at least one uppercase letter, one lowercase letter, and one number.
    const response = await apiClient.register(email, password, name);
    // Auto-login after registration
    await login(email, password);
  };

  const logout = async () => {
    await apiClient.logout();
    setUser(null);
    setRefreshToken(null);
    localStorage.removeItem('refresh_token');
    apiClient.setToken(null);
  };

  useEffect(() => {
    if (!refreshToken) return;

    const interval = setInterval(async () => {
      try {
        const newTokens = await apiClient.refreshToken(refreshToken);
        apiClient.setToken(newTokens.access_token);
        setRefreshToken(newTokens.refresh_token);
        localStorage.setItem('refresh_token', newTokens.refresh_token);
      } catch (error) {
        console.error('Failed to refresh token', error);
        // Optionally, logout the user if refresh fails
        logout();
      }
    }, 15 * 60 * 1000); // 15 minutes

    return () => clearInterval(interval);
  }, [refreshToken]);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, refreshToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
