import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
// TODO: Update imports once API is generated
// import { usePostAuthLogin, usePostAuthRegister, usePostAuthRefresh, useGetAuthMe, usePostAuthLogout } from '@/lib/api/generated';
// import type { UserResponse, TokenResponse, UserCreate, TokenRefreshRequest } from '@/lib/api/generated';
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

const AUTH_TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);

  // TODO: Use generated hooks once API is generated:
  // const loginMutation = usePostAuthLogin();
  // const registerMutation = usePostAuthRegister();
  // const refreshMutation = usePostAuthRefresh();
  // const getMeQuery = useGetAuthMe();
  // const logoutMutation = usePostAuthLogout();

  // Restore session on mount
  useEffect(() => {
    const restoreSession = async () => {
      try {
        const storedToken = localStorage.getItem(AUTH_TOKEN_KEY);
        const storedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

        if (storedToken) {
          // Token is injected via mutator, no need to set it on a client
          
          // Try to get user data with stored token
          // TODO: Use generated hook: const { data: userData } = await getMeQuery.refetch();
          try {
            // Placeholder - will use generated hook after generation
            const userData = null as any; // await getMeQuery.refetch().then(r => r.data);
            if (userData) {
              setUser(userData);
              if (storedRefreshToken) {
                setRefreshToken(storedRefreshToken);
              }
              setIsLoading(false);
              return;
            }
          } catch (error) {
            // Token might be expired, try refresh
            console.log('Access token expired, attempting refresh...');
          }
        }

        // If no token or token expired, try refresh token
        if (storedRefreshToken) {
          try {
            // TODO: Use generated hook: const { data: newTokens } = await refreshMutation.mutateAsync({ refresh_token: storedRefreshToken });
            const newTokens = null as any; // await refreshMutation.mutateAsync({ refresh_token: storedRefreshToken });
            if (newTokens) {
              localStorage.setItem(AUTH_TOKEN_KEY, newTokens.access_token);
              localStorage.setItem(REFRESH_TOKEN_KEY, newTokens.refresh_token);
              setRefreshToken(newTokens.refresh_token);
              
              // Get user data with new token
              // TODO: Use generated hook
              const userData = null as any; // await getMeQuery.refetch().then(r => r.data);
              if (userData) {
                setUser(userData);
              }
              setIsLoading(false);
              return;
            }
          } catch (error) {
            console.error('Failed to refresh token:', error);
            // Clear invalid tokens
            localStorage.removeItem(AUTH_TOKEN_KEY);
            localStorage.removeItem(REFRESH_TOKEN_KEY);
          }
        }
      } catch (error) {
        console.error('Error restoring session:', error);
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, []);

  const login = async (email: string, password: string) => {
    // TODO: Replace with generated hook after generation:
    // const response = await loginMutation.mutateAsync({
    //   username: email, // OAuth2PasswordRequestForm uses 'username' field
    //   password: password,
    // });
    const response = null as any;
    
    // Store tokens in localStorage for persistence
    if (response?.access_token) {
      localStorage.setItem(AUTH_TOKEN_KEY, response.access_token);
    }
    if (response?.refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
      setRefreshToken(response.refresh_token);
    }
    
    // TODO: Get user data via generated hook after login
    // const userData = await getMeQuery.refetch().then(r => r.data);
    if (response?.user) {
      setUser(response.user);
    }
  };

  const register = async (email: string, password: string, name: string) => {
    // TODO: Replace with generated hook after generation:
    // const response = await registerMutation.mutateAsync({ email, password, name });
    const response = null as any;
    // Auto-login after registration
    await login(email, password);
  };

  const logout = async () => {
    try {
      // TODO: Replace with generated hook after generation:
      // await logoutMutation.mutateAsync();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setRefreshToken(null);
      localStorage.removeItem(AUTH_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
    }
  };

  // Auto-refresh token before it expires (check every hour since tokens last 7 days)
  useEffect(() => {
    if (!refreshToken) return;

    const refreshInterval = setInterval(async () => {
      try {
        // TODO: Use generated hook after generation:
        // const { data: newTokens } = await refreshMutation.mutateAsync({ refresh_token: refreshToken });
        const newTokens = null as any;
        if (newTokens) {
          localStorage.setItem(AUTH_TOKEN_KEY, newTokens.access_token);
          localStorage.setItem(REFRESH_TOKEN_KEY, newTokens.refresh_token);
          setRefreshToken(newTokens.refresh_token);
          console.log('Token refreshed successfully');
        }
      } catch (error) {
        console.error('Failed to refresh token:', error);
        // Don't logout automatically - let the next request handle it
      }
    }, 60 * 60 * 1000); // Check every hour

    return () => clearInterval(refreshInterval);
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
