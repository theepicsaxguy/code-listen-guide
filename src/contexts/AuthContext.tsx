import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from 'react';
import { useLogin, useRegister, useRefreshToken, useGetMe, useLogout } from '@/lib/api/generated';
import { User } from '@/lib/types';
import {
  getPasskeyAuthenticationOptions,
  authenticatePasskey as authenticatePasskeyAPI,
  getPasskeyRegistrationOptions,
  registerPasskey as registerPasskeyAPI,
  listPasskeys,
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
  loginWithPasskey: (email?: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  registerPasskey: (name?: string) => Promise<void>;
  logout: () => Promise<void>;
  showPasskeyPrompt: boolean;
  setShowPasskeyPrompt: (show: boolean) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showPasskeyPrompt, setShowPasskeyPrompt] = useState(false);

  const loginMutation = useLogin();
  const registerMutation = useRegister();
  const refreshMutation = useRefreshToken();
  const getMeQuery = useGetMe({ query: { enabled: false } });
  const logoutMutation = useLogout();

  const checkAndShowPasskeyPrompt = useCallback(async () => {
    const dismissed = localStorage.getItem('passkey_prompt_dismissed') === 'true';
    if (dismissed) {
      return;
    }

    if (!isWebAuthnSupported()) {
      return;
    }

    try {
      const passkeys = await listPasskeys();
      const activePasskeys = passkeys.filter(p => p.is_active);

      if (activePasskeys.length === 0) {
        setShowPasskeyPrompt(true);
      }
    } catch (error) {
      console.error('Failed to check passkeys:', error);
    }
  }, [setShowPasskeyPrompt]);

  // Restore session on mount
  const restoreSession = useCallback(async () => {
    let restored = false;

    try {
      const result = await getMeQuery.refetch();
      if (result.data) {
        setUser(result.data as unknown as User);
        await checkAndShowPasskeyPrompt();
        restored = true;
      }
    } catch (error) {
      console.error('Failed to load current user:', error);
    }

    if (!restored) {
      try {
        const newTokens = await refreshMutation.mutateAsync();
        if (newTokens) {
          const userResult = await getMeQuery.refetch();
          if (userResult.data) {
            setUser(userResult.data as unknown as User);
            await checkAndShowPasskeyPrompt();
            restored = true;
          }
        }
      } catch (error) {
        console.error('Failed to refresh session:', error);
        setUser(null);
      }
    }

    setIsLoading(false);
  }, [checkAndShowPasskeyPrompt, getMeQuery, refreshMutation]);

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  const login = async (email: string, password: string) => {
    await loginMutation.mutateAsync({
      data: {
        username: email, // OAuth2PasswordRequestForm uses 'username' field
        password: password,
      },
    });

    // Get user data via generated hook after login
    const userResult = await getMeQuery.refetch();
    if (userResult.data) {
      setUser(userResult.data as unknown as User);
      // Check for passkeys and show prompt if needed
      await checkAndShowPasskeyPrompt();
    }
  };

  const register = async (email: string, password: string, name: string) => {
    const response = await registerMutation.mutateAsync({
      data: { email, password, name },
    });
    // Auto-login after registration
    await login(email, password);
  };

  const loginWithPasskey = async (email?: string) => {
    if (!isWebAuthnSupported()) {
      throw new Error('WebAuthn is not supported in this browser');
    }

    // Get authentication options (with or without email for conditional UI)
    const authOptions = await getPasskeyAuthenticationOptions(email);

    // Authenticate with passkey
    const credential = await authenticatePasskeyWebAuthn(authOptions.options);

    // Convert credential to JSON
    const credentialJSON = credentialToJSON(credential);

    // Complete authentication
    await authenticatePasskeyAPI({
      authentication_response: credentialJSON,
      challenge: authOptions.challenge,
      credential_id: credentialJSON.id,
    });

    // Get user data
    const userResult = await getMeQuery.refetch();
    if (userResult.data) {
      setUser(userResult.data as unknown as User);
      // Check for passkeys and show prompt if needed
      await checkAndShowPasskeyPrompt();
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

    // Hide the prompt after successful registration
    setShowPasskeyPrompt(false);
    // Clear the dismissal flag so they can see it again if they delete all passkeys
    localStorage.removeItem('passkey_prompt_dismissed');
  };

  const logout = async () => {
    try {
      await logoutMutation.mutateAsync();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setShowPasskeyPrompt(false);
    }
  };

  // Auto-refresh token before it expires (check every hour since tokens last 7 days)
  useEffect(() => {
    const refreshInterval = setInterval(async () => {
      try {
        await refreshMutation.mutateAsync();
        console.log('Token refreshed successfully');
      } catch (error) {
        console.error('Failed to refresh token:', error);
        // Don't logout automatically - let the next request handle it
      }
    }, 60 * 60 * 1000); // Check every hour

    return () => clearInterval(refreshInterval);
  }, [refreshMutation, user]);

  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      login, 
      loginWithPasskey, 
      register,
      registerPasskey,
      logout,
      showPasskeyPrompt,
      setShowPasskeyPrompt,
    }}>
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
