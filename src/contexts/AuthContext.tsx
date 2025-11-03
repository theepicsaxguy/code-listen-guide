import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { 
  useLogin,
  useRegister,
  useRefreshToken,
  useGetMe,
  useLogout,
} from '@/lib/api/generated';
import type { UserResponse, TokenResponse, TokenRefreshRequest } from '@/lib/api/generated';
import { User } from '@/lib/types';
import {
  getPasskeyAuthenticationOptions,
  authenticatePasskey as authenticatePasskeyAPI,
  getPasskeyRegistrationOptions,
  registerPasskey as registerPasskeyAPI,
} from '@/lib/api/passkeys';
import {
  authenticatePasskey as authenticatePasskeyWebAuthn,
  registerPasskey as registerPasskeyWebAuthn,
  credentialToJSON,
  isWebAuthnSupported,
} from '@/lib/webauthn';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithPasskey: (email: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  registerPasskey: (name?: string) => Promise<void>;
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

  const loginMutation = useLogin();
  const registerMutation = useRegister();
  const refreshMutation = useRefreshToken();
  const getMeQuery = useGetMe({ query: { enabled: false } });
  const logoutMutation = useLogout();

  // Restore session on mount
  useEffect(() => {
    const restoreSession = async () => {
      try {
        const storedToken = localStorage.getItem(AUTH_TOKEN_KEY);
        const storedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

        if (storedToken) {
          // Try to get user data with stored token
          try {
            const result = await getMeQuery.refetch();
            if (result.data) {
              setUser(result.data as unknown as User);
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
            const newTokens = await refreshMutation.mutateAsync({
              data: { refresh_token: storedRefreshToken },
            });
            if (newTokens) {
              localStorage.setItem(AUTH_TOKEN_KEY, newTokens.access_token);
              localStorage.setItem(REFRESH_TOKEN_KEY, newTokens.refresh_token);
              setRefreshToken(newTokens.refresh_token);
              
              // Get user data with new token
              const userResult = await getMeQuery.refetch();
              if (userResult.data) {
                setUser(userResult.data as unknown as User);
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
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const login = async (email: string, password: string) => {
    const response = await loginMutation.mutateAsync({
      data: {
        username: email, // OAuth2PasswordRequestForm uses 'username' field
        password: password,
      },
    });
    
    // Store tokens in localStorage for persistence
    if (response?.access_token) {
      localStorage.setItem(AUTH_TOKEN_KEY, response.access_token);
    }
    if (response?.refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
      setRefreshToken(response.refresh_token);
    }
    
    // Get user data via generated hook after login
    const userResult = await getMeQuery.refetch();
    if (userResult.data) {
      setUser(userResult.data as unknown as User);
    }
  };

  const register = async (email: string, password: string, name: string) => {
    const response = await registerMutation.mutateAsync({
      data: { email, password, name },
    });
    // Auto-login after registration
    await login(email, password);
  };

  const loginWithPasskey = async (email: string) => {
    if (!isWebAuthnSupported()) {
      throw new Error('WebAuthn is not supported in this browser');
    }

    // Get authentication options
    const authOptions = await getPasskeyAuthenticationOptions(email);

    // Authenticate with passkey
    const credential = await authenticatePasskeyWebAuthn(authOptions.options);

    // Convert credential to JSON
    const credentialJSON = credentialToJSON(credential);

    // Complete authentication
    const tokenResponse = await authenticatePasskeyAPI({
      authentication_response: credentialJSON,
      challenge: authOptions.challenge,
      credential_id: credentialJSON.id,
    });

    // Store tokens
    if (tokenResponse?.access_token) {
      localStorage.setItem(AUTH_TOKEN_KEY, tokenResponse.access_token);
    }
    if (tokenResponse?.refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, tokenResponse.refresh_token);
      setRefreshToken(tokenResponse.refresh_token);
    }

    // Get user data
    const userResult = await getMeQuery.refetch();
    if (userResult.data) {
      setUser(userResult.data as unknown as User);
    }
  };

  const registerPasskey = async (name?: string) => {
    if (!isWebAuthnSupported()) {
      throw new Error('WebAuthn is not supported in this browser');
    }

    // Get registration options
    const regOptions = await getPasskeyRegistrationOptions(name);

    // Register passkey using WebAuthn API
    const credential = await registerPasskeyWebAuthn(regOptions.options);

    // Convert credential to JSON
    const credentialJSON = credentialToJSON(credential);

    // Complete registration
    await registerPasskeyAPI({
      registration_response: credentialJSON,
      challenge: regOptions.challenge,
      name,
    });
  };

  const logout = async () => {
    try {
      await logoutMutation.mutateAsync();
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
        const newTokens = await refreshMutation.mutateAsync({
          data: { refresh_token: refreshToken },
        });
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
  }, [refreshToken, refreshMutation]);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, loginWithPasskey, register, registerPasskey, logout, refreshToken }}>
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
