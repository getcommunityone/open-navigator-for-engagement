import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: number;
  email: string;
  username?: string;
  full_name?: string;
  avatar_url?: string;
  oauth_provider?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (provider: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const API_URL = import.meta.env.PROD 
    ? '/api'
    : 'http://localhost:8000';

  // Load user from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    console.log('🔐 Auth initialization - Token found:', !!storedToken);
    
    if (storedToken) {
      setToken(storedToken);
      fetchUser(storedToken);
    } else {
      setIsLoading(false);
    }

    // Check for token in URL (OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');
    if (urlToken) {
      console.log('🔐 OAuth callback - Token received from URL');
      localStorage.setItem('auth_token', urlToken);
      setToken(urlToken);
      fetchUser(urlToken);
      
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const fetchUser = async (authToken: string) => {
    try {
      console.log('🔐 Fetching user data from:', `${API_URL}/auth/me`);
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        console.log('✅ User data loaded:', userData.email);
        setUser(userData);
      } else {
        console.error('❌ Failed to fetch user:', response.status, response.statusText);
        // Token is invalid
        localStorage.removeItem('auth_token');
        setToken(null);
      }
    } catch (error) {
      console.error('❌ Error fetching user:', error);
      localStorage.removeItem('auth_token');
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = (provider: string) => {
    // Redirect to OAuth endpoint
    const redirectUri = encodeURIComponent(window.location.origin);
    window.location.href = `${API_URL}/auth/login/${provider}?redirect_uri=${redirectUri}`;
  };

  const logout = () => {
    console.log('🔐 Logging out - removing token');
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isAuthenticated: !!user,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
