import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../api/auth';

// Create Auth Context
const AuthContext = createContext();

// Custom hook to use Auth Context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [tokens, setTokens] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshTimeout, setRefreshTimeout] = useState(null);

  // Check if user is authenticated
  const isAuthenticated = useCallback(() => {
    return tokens !== null && user !== null;
  }, [tokens, user]);

  // Get user role
  const getUserRole = useCallback(() => {
    return user?.role || null;
  }, [user]);

  // Login function
  const login = async (username, password) => {
    try {
      setLoading(true);
      const response = await authAPI.login(username, password);

      const { access, refresh, user: userData } = response;

      // Store tokens in both memory and localStorage
      const tokenData = { access, refresh };
      setTokens(tokenData);
      setUser(userData);
      localStorage.setItem('tokens', JSON.stringify(tokenData));
      localStorage.setItem('user', JSON.stringify(userData));

      // Schedule automatic token refresh (refresh 5 minutes before expiry)
      scheduleTokenRefresh(access);

      setLoading(false);
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);

      // Handle different error formats from backend
      let errorMessage = 'Invalid username or password';

      if (error && typeof error === 'object') {
        // Handle Django REST framework error format
        if (error.non_field_errors && Array.isArray(error.non_field_errors)) {
          errorMessage = error.non_field_errors[0];
        } else if (error.username && Array.isArray(error.username)) {
          errorMessage = error.username[0];
        } else if (error.password && Array.isArray(error.password)) {
          errorMessage = error.password[0];
        } else if (error.detail) {
          errorMessage = error.detail;
        } else if (error.error) {
          errorMessage = error.error;
        } else if (typeof error === 'string') {
          errorMessage = error;
        }
      } else if (typeof error === 'string') {
        errorMessage = error;
      }

      setLoading(false);
      return {
        success: false,
        error: errorMessage
      };
    }
  };

  // Logout function
  const logout = () => {
    setTokens(null);
    setUser(null);
    localStorage.removeItem('tokens');
    localStorage.removeItem('user');
    if (refreshTimeout) {
      clearTimeout(refreshTimeout);
      setRefreshTimeout(null);
    }
  };

  // Schedule automatic token refresh
  const scheduleTokenRefresh = (accessToken) => {
    try {
      // Safely decode JWT to get expiry time
      const payload = safeDecodeToken(accessToken);
      
      if (!payload || !payload.exp) {
        console.warn('Invalid token payload or missing exp');
        logout();
        return;
      }

      const expiryTime = payload.exp * 1000; // Convert to milliseconds
      const currentTime = Date.now();

      // Refresh 5 minutes before expiry
      const refreshTime = expiryTime - currentTime - (5 * 60 * 1000);

      if (refreshTime > 0) {
        if (refreshTimeout) {
          clearTimeout(refreshTimeout);
        }

        const timeout = setTimeout(async () => {
          // Inline refresh logic to avoid circular dependency
          const storedTokens = localStorage.getItem('tokens');
          if (!storedTokens) {
            logout();
            return;
          }
          
          try {
            const parsedTokens = JSON.parse(storedTokens);
            const response = await authAPI.refreshToken(parsedTokens.refresh);
            const newAccessToken = response.access;
            
            const newTokens = { ...parsedTokens, access: newAccessToken };
            setTokens(newTokens);
            localStorage.setItem('tokens', JSON.stringify(newTokens));
            
            // Schedule next refresh
            scheduleTokenRefresh(newAccessToken);
          } catch (error) {
            console.error('Token refresh failed:', error);
            logout();
          }
        }, refreshTime);

        setRefreshTimeout(timeout);
      } else {
        // Token is already expired or will expire soon, refresh immediately
        (async () => {
          const storedTokens = localStorage.getItem('tokens');
          if (!storedTokens) {
            logout();
            return;
          }
          
          try {
            const parsedTokens = JSON.parse(storedTokens);
            const response = await authAPI.refreshToken(parsedTokens.refresh);
            const newAccessToken = response.access;
            
            const newTokens = { ...parsedTokens, access: newAccessToken };
            setTokens(newTokens);
            localStorage.setItem('tokens', JSON.stringify(newTokens));
          } catch (error) {
            console.error('Token refresh failed:', error);
            logout();
          }
        })();
      }
    } catch (error) {
      console.error('Error scheduling token refresh:', error);
      logout();
    }
  };

  // Refresh access token
  const refreshAccessToken = async () => {
    if (!tokens?.refresh) {
      logout();
      return false;
    }

    try {
      const response = await authAPI.refreshToken(tokens.refresh);
      const newAccessToken = response.access;

      // Validate new token before storing
      const payload = safeDecodeToken(newAccessToken);
      if (!payload || !payload.exp) {
        console.warn('Received invalid token from refresh, logging out');
        logout();
        return false;
      }

      const newTokens = { ...tokens, access: newAccessToken };
      setTokens(newTokens);
      localStorage.setItem('tokens', JSON.stringify(newTokens));
      
      // Schedule next refresh
      scheduleTokenRefresh(newAccessToken);

      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
      return false;
    }
  };

  // Safely decode JWT token
  const safeDecodeToken = (token) => {
    try {
      // Validate token format
      if (!token || typeof token !== 'string') {
        console.warn('Invalid token type');
        return null;
      }

      // Check if token has the correct JWT format (3 parts separated by dots)
      const parts = token.split('.');
      if (parts.length !== 3) {
        console.warn('Invalid JWT format: expected 3 parts');
        return null;
      }

      // Safely decode the payload
      try {
        const payload = JSON.parse(atob(parts[1]));
        return payload;
      } catch (decodeError) {
        console.warn('Failed to decode JWT payload:', decodeError);
        return null;
      }
    } catch (error) {
      console.warn('Error in safeDecodeToken:', error);
      return null;
    }
  };

  // Initialize auth state on app load
  useEffect(() => {
    console.log('[AuthContext] Initializing auth...');
    
    const initializeAuth = async () => {
      try {
        // Try to restore tokens from localStorage
        const storedTokens = localStorage.getItem('tokens');
        const storedUser = localStorage.getItem('user');

        console.log('[AuthContext] Stored tokens:', storedTokens ? 'exists' : 'none');
        console.log('[AuthContext] Stored user:', storedUser ? 'exists' : 'none');

        if (storedTokens && storedUser) {
          try {
            const parsedTokens = JSON.parse(storedTokens);
            const parsedUser = JSON.parse(storedUser);

            // Safely verify token is not expired
            const payload = safeDecodeToken(parsedTokens.access);
            
            if (!payload || !payload.exp) {
              // Invalid token format, clear and proceed
              console.warn('[AuthContext] Stored token has invalid format, clearing');
              localStorage.removeItem('tokens');
              localStorage.removeItem('user');
              // Don't return early - let finally block handle setLoading(false)
            } else {
              const expiryTime = payload.exp * 1000;
              const currentTime = Date.now();

              if (currentTime < expiryTime) {
                // Token is still valid
                console.log('[AuthContext] Token is valid, restoring session');
                setTokens(parsedTokens);
                setUser(parsedUser);
                scheduleTokenRefresh(parsedTokens.access);
              } else {
                // Token expired, try to refresh
                console.log('[AuthContext] Token expired, attempting refresh');
                try {
                  const response = await authAPI.refreshToken(parsedTokens.refresh);
                  const newAccessToken = response.access;
                  const newTokens = { ...parsedTokens, access: newAccessToken };
                  setTokens(newTokens);
                  setUser(parsedUser);
                  localStorage.setItem('tokens', JSON.stringify(newTokens));
                  scheduleTokenRefresh(newAccessToken);
                  console.log('[AuthContext] Token refresh successful');
                } catch (error) {
                  // Refresh failed, clear stored data
                  console.warn('[AuthContext] Token refresh failed, clearing stored tokens');
                  localStorage.removeItem('tokens');
                  localStorage.removeItem('user');
                }
              }
            }
          } catch (parseError) {
            // JSON parse error or other issue, clear corrupted data
            console.warn('[AuthContext] Error parsing stored auth data, clearing:', parseError);
            localStorage.removeItem('tokens');
            localStorage.removeItem('user');
          }
        } else {
          console.log('[AuthContext] No stored tokens found');
        }
      } catch (error) {
        console.error('[AuthContext] Error initializing auth:', error);
        // Ensure we clear any potentially corrupted data
        try {
          localStorage.removeItem('tokens');
          localStorage.removeItem('user');
        } catch (e) {
          console.error('[AuthContext] Error clearing localStorage:', e);
        }
      } finally {
        console.log('[AuthContext] Setting loading to false');
        setLoading(false);
      }
    };

    initializeAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (refreshTimeout) {
        clearTimeout(refreshTimeout);
      }
    };
  }, [refreshTimeout]);

  const value = {
    tokens,
    user,
    loading,
    isAuthenticated,
    getUserRole,
    login,
    logout,
    refreshAccessToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;