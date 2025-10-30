import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/lib/api';
import { User } from '@/lib/types';

interface AdminAuthContextType {
  admin: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AdminAuthContext = createContext<AdminAuthContextType | undefined>(undefined);

export function AdminAuthProvider({ children }: { children: ReactNode }) {
  const [admin, setAdmin] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if admin is logged in on mount
    const token = localStorage.getItem('admin_token');

    if (token) {
      apiClient.setToken(token);
      apiClient
        .getMe()
        .then((userData) => {
          // Verify user has admin privileges
          // The backend should return is_admin or role information
          setAdmin(userData);
        })
        .catch(() => {
          localStorage.removeItem('admin_token');
          apiClient.setToken(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await apiClient.login(email, password);
    
    // Store token in admin-specific localStorage key
    localStorage.setItem('admin_token', response.access_token);
    apiClient.setToken(response.access_token);
    
    // Verify admin access by fetching user data
    const userData = await apiClient.getMe();
    setAdmin(userData);
  };

  const logout = async () => {
    await apiClient.logout();
    setAdmin(null);
    localStorage.removeItem('admin_token');
    apiClient.setToken(null);
  };

  return (
    <AdminAuthContext.Provider value={{ admin, isLoading, login, logout }}>
      {children}
    </AdminAuthContext.Provider>
  );
}

export function useAdminAuth() {
  const context = useContext(AdminAuthContext);
  if (context === undefined) {
    throw new Error('useAdminAuth must be used within an AdminAuthProvider');
  }
  return context;
}
