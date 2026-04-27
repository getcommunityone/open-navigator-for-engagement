import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: number;
  email: string;
  username?: string;
  full_name?: string;
  avatar_url?: string;
  oauth_provider?: string;
  state?: string;
  county?: string;
  city?: string;
  school_board?: string;
  profile_completed?: boolean;
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
    // Check for token in URL FIRST (OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');
    
    if (urlToken) {
      localStorage.setItem('auth_token', urlToken);
      setToken(urlToken);
      fetchUser(urlToken);
      
      // Clean URL (remove token from address bar)
      window.history.replaceState({}, document.title, window.location.pathname);
      return; // Exit early, fetchUser will handle loading state
    }
    
    // Check for stored token
    const storedToken = localStorage.getItem('auth_token');
    
    if (storedToken) {
      setToken(storedToken);
      fetchUser(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUser = async (authToken: string) => {
    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Token is invalid
        localStorage.removeItem('auth_token');
        setToken(null);
      }
    } catch (error) {
      console.error('Error fetching user:', error);
      localStorage.removeItem('auth_token');
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = (provider: string) => {
    // Redirect to OAuth endpoint
    const redirectUri = encodeURIComponent(window.location.origin);
    const authUrl = `${API_URL}/auth/login/${provider}?redirect_uri=${redirectUri}`;
    window.location.href = authUrl;
  };

  const logout = () => {
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
