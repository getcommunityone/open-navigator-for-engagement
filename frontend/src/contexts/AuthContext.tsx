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
    console.log('🔐 Auth initialization starting...');
    console.log('🔐 Current URL:', window.location.href);
    
    // Check for token in URL FIRST (OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');
    
    if (urlToken) {
      console.log('🔐 OAuth callback - Token received from URL');
      console.log('🔐 Token preview:', urlToken.substring(0, 20) + '...');
      localStorage.setItem('auth_token', urlToken);
      setToken(urlToken);
      fetchUser(urlToken);
      
      // Clean URL (remove token from address bar)
      window.history.replaceState({}, document.title, window.location.pathname);
      return; // Exit early, fetchUser will handle loading state
    }
    
    // Check for stored token
    const storedToken = localStorage.getItem('auth_token');
    console.log('🔐 Stored token found:', !!storedToken);
    
    if (storedToken) {
      console.log('🔐 Token preview:', storedToken.substring(0, 20) + '...');
      setToken(storedToken);
      fetchUser(storedToken);
    } else {
      console.log('🔐 No token found - user not authenticated');
      setIsLoading(false);
    }
  }, []);

  // Debug: Log user state changes
  useEffect(() => {
    console.log('🔐 User state changed:', {
      user: user ? { id: user.id, email: user.email } : null,
      isAuthenticated: !!user,
      token: token ? token.substring(0, 20) + '...' : null,
    });
  }, [user, token]);

  const fetchUser = async (authToken: string) => {
    try {
      console.log('🔐 Fetching user data from:', `${API_URL}/auth/me`);
      console.log('🔐 Using token:', authToken.substring(0, 30) + '...');
      
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      console.log('🔐 Response status:', response.status);
      console.log('🔐 Response headers:', Object.fromEntries(response.headers.entries()));

      if (response.ok) {
        const userData = await response.json();
        console.log('✅ User data loaded:', userData);
        console.log('✅ Setting user state with:', {
          id: userData.id,
          email: userData.email,
          avatar_url: userData.avatar_url,
          full_name: userData.full_name,
        });
        setUser(userData);
      } else {
        const errorText = await response.text();
        console.error('❌ Failed to fetch user:', response.status, response.statusText);
        console.error('❌ Error details:', errorText);
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
      console.log('🔐 Loading complete. User:', user ? user.email : 'null');
    }
  };

  const login = (provider: string) => {
    console.log('🔐 Starting OAuth flow for provider:', provider);
    // Redirect to OAuth endpoint
    const redirectUri = encodeURIComponent(window.location.origin);
    const authUrl = `${API_URL}/auth/login/${provider}?redirect_uri=${redirectUri}`;
    console.log('🔐 Redirecting to:', authUrl);
    window.location.href = authUrl;
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
