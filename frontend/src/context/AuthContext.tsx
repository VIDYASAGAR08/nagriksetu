import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, CitizenProfile } from '../types';
import { api, setAuthToken, getAuthToken } from '../services/api';

interface AuthContextType {
  user: User | null;
  citizenProfile: CitizenProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isCitizen: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (payload: any) => Promise<User>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  highContrast: boolean;
  largeText: boolean;
  toggleHighContrast: () => void;
  toggleLargeText: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [citizenProfile, setCitizenProfile] = useState<CitizenProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Accessibility States
  const [highContrast, setHighContrast] = useState<boolean>(
    localStorage.getItem('civic_contrast') === 'true'
  );
  const [largeText, setLargeText] = useState<boolean>(
    localStorage.getItem('civic_largetext') === 'true'
  );

  const toggleHighContrast = () => {
    setHighContrast(prev => {
      const next = !prev;
      localStorage.setItem('civic_contrast', String(next));
      return next;
    });
  };

  const toggleLargeText = () => {
    setLargeText(prev => {
      const next = !prev;
      localStorage.setItem('civic_largetext', String(next));
      return next;
    });
  };

  // Sync accessibility classes with document body
  useEffect(() => {
    if (highContrast) {
      document.documentElement.classList.add('high-contrast');
    } else {
      document.documentElement.classList.remove('high-contrast');
    }

    if (largeText) {
      document.documentElement.classList.add('font-size-large');
    } else {
      document.documentElement.classList.remove('font-size-large');
    }
  }, [highContrast, largeText]);

  const refreshUser = async () => {
    try {
      const data = await api.auth.me();
      setUser(data.user);
      setCitizenProfile(data.citizen_profile || null);
    } catch (err) {
      setUser(null);
      setCitizenProfile(null);
      setAuthToken(null);
    }
  };

  // On initial mount, verify session if token exists
  useEffect(() => {
    const initAuth = async () => {
      const token = getAuthToken();
      if (token) {
        await refreshUser();
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email: string, password: string): Promise<User> => {
    const res = await api.auth.login({ email, password });
    setAuthToken(res.access_token);
    setUser(res.user);
    // Fetch profile details
    await refreshUser();
    return res.user;
  };

  const register = async (payload: any): Promise<User> => {
    const res = await api.auth.register(payload);
    setAuthToken(res.access_token);
    setUser(res.user);
    await refreshUser();
    return res.user;
  };

  const logout = async () => {
    try {
      await api.auth.logout();
    } catch (e) {
      // Proceed with local logout regardless of network status
    }
    setAuthToken(null);
    setUser(null);
    setCitizenProfile(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        citizenProfile,
        isLoading,
        isAuthenticated: !!user,
        isAdmin: user?.role === 'admin',
        isCitizen: user?.role === 'citizen',
        login,
        register,
        logout,
        refreshUser,
        highContrast,
        largeText,
        toggleHighContrast,
        toggleLargeText,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
