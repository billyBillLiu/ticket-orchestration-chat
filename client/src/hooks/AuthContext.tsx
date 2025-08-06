import {
  useRef,
  useMemo,
  useState,
  useEffect,
  ReactNode,
  useContext,
  useCallback,
  createContext,
} from 'react';
import { useRecoilState } from 'recoil';
import { useNavigate } from 'react-router-dom';
import { setTokenHeader, SystemRoles, QueryKeys } from 'librechat-data-provider';
import type * as t from 'librechat-data-provider';
import {
  useGetRole,
  useGetUserQuery,
  useLoginUserMutation,
  useLogoutUserMutation,
  useRefreshTokenMutation,
} from '~/data-provider';
import { QueryClient } from '@tanstack/react-query';
import { TAuthConfig, TUserContext, TAuthContext, TResError } from '~/common';
import useTimeout from './useTimeout';
import store from '~/store';

const AuthContext = createContext<TAuthContext | undefined>(undefined);

// Token persistence utilities
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

const getStoredToken = (): string | undefined => {
  try {
    return localStorage.getItem(TOKEN_KEY) || undefined;
  } catch (error) {
    console.error('Error reading token from localStorage:', error);
    return undefined;
  }
};

const setStoredToken = (token: string | undefined): void => {
  try {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  } catch (error) {
    console.error('Error writing token to localStorage:', error);
  }
};

const getStoredUser = (): t.TUser | undefined => {
  try {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : undefined;
  } catch (error) {
    console.error('Error reading user from localStorage:', error);
    return undefined;
  }
};

const setStoredUser = (user: t.TUser | undefined): void => {
  try {
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(USER_KEY);
    }
  } catch (error) {
    console.error('Error writing user to localStorage:', error);
  }
};

const clearStoredAuth = (): void => {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch (error) {
    console.error('Error clearing auth from localStorage:', error);
  }
};

const AuthContextProvider = ({
  authConfig,
  children,
}: {
  authConfig?: TAuthConfig;
  children: ReactNode;
}) => {
  const [user, setUser] = useRecoilState(store.user);
  const [token, setToken] = useState<string | undefined>(undefined);
  const [error, setError] = useState<string | undefined>(undefined);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isInitialized, setIsInitialized] = useState<boolean>(false);
  const logoutRedirectRef = useRef<string | undefined>(undefined);
  const refreshAttemptedRef = useRef<boolean>(false);

  const { data: userRole = null } = useGetRole(SystemRoles.USER, {
    enabled: !!(isAuthenticated && (user?.role ?? '')),
  });
  const { data: adminRole = null } = useGetRole(SystemRoles.ADMIN, {
    enabled: !!(isAuthenticated && user?.role === SystemRoles.ADMIN),
  });

  const navigate = useNavigate();

  const setUserContext = useCallback((userContext: TUserContext) => {
    const { token, isAuthenticated, user, redirect } = userContext;
    
    console.log('🔧 setUserContext called with:', { token: !!token, isAuthenticated, user: !!user, redirect });
    
    // Update state
    setUser(user);
    setToken(token);
    setIsAuthenticated(isAuthenticated);
    
    // Persist to localStorage
    setStoredToken(token);
    setStoredUser(user);
    
    // Set token header for API requests
    setTokenHeader(token || '');

    // Use a custom redirect if set
    const finalRedirect = logoutRedirectRef.current || redirect;
    // Clear the stored redirect
    logoutRedirectRef.current = undefined;

    if (finalRedirect == null) {
      return;
    }

    console.log('🔧 Navigating to:', finalRedirect);
    if (finalRedirect.startsWith('http://') || finalRedirect.startsWith('https://')) {
      window.location.href = finalRedirect;
    } else {
      navigate(finalRedirect, { replace: true });
    }
  }, [navigate]);
  const doSetError = useTimeout({ callback: (error) => setError(error as string | undefined) });

  const loginUser = useLoginUserMutation({
    onSuccess: (data: t.TLoginResponse) => {
      const { user, token, twoFAPending, tempToken } = data;
      if (twoFAPending) {
        // Redirect to the two-factor authentication route.
        navigate(`/login/2fa?tempToken=${tempToken}`, { replace: true });
        return;
      }
      setError(undefined);
      setUserContext({ token, isAuthenticated: true, user, redirect: '/c/new' });
    },
    onError: (error: TResError | unknown) => {
      const resError = error as TResError;
      doSetError(resError.message);
      navigate('/login', { replace: true });
    },
  });
  const logoutUser = useLogoutUserMutation({
    onSuccess: (data) => {
      // Clear stored auth data
      clearStoredAuth();
      setUserContext({
        token: undefined,
        isAuthenticated: false,
        user: undefined,
        redirect: '/login',
      });
    },
    onError: (error) => {
      // Clear stored auth data on error too
      clearStoredAuth();
      doSetError((error as Error).message);
      setUserContext({
        token: undefined,
        isAuthenticated: false,
        user: undefined,
        redirect: '/login',
      });
    },
  });
  const refreshToken = useRefreshTokenMutation();

  const logout = useCallback(
    (redirect?: string) => {
      if (redirect) {
        logoutRedirectRef.current = redirect;
      }
      logoutUser.mutate(undefined);
    },
    [logoutUser],
  );

  const userQuery = useGetUserQuery({ enabled: !!(token ?? '') });

  const login = (data: t.TLoginUser) => {
    fetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: data.email, password: data.password }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(async (res) => {
        const result = await res.json();
        console.log('🔧 Login response:', result);
        
        // Handle both old and new response formats
        if (result.success === false) {
          const error = result.message;
          throw new Error(error);
        }
        
        // Check if it's the new standardized response format
        if (result.success && result.data) {
          return result.data;
        }
        
        // Handle direct response format (from backend)
        return result;
      })
      .then((result) => {
        // Directly set user context here, do not call loginUser.mutate
        const { user, token, token_type } = result;
        console.log('🔧 Login successful, setting user context');
        
        // Update state immediately
        setUser(user);
        setToken(token);
        setIsAuthenticated(true);
        
        // Persist to localStorage
        setStoredToken(token);
        setStoredUser(user);
        
        // Set token header for API requests
        setTokenHeader(token || '');
        
        // Clear any stale conversation cache
        // Note: We can't access the query client here, so we'll rely on the
        // conversation queries to handle fresh data loading
        
        setError(undefined);
        refreshAttemptedRef.current = false; // Reset flag on successful login
        
        // Navigate directly instead of using setUserContext
        console.log('🔧 Navigating to /c/new after successful login');
        navigate('/c/new', { replace: true });
      })
      .catch((error) => {
        doSetError(error.message);
        navigate('/login', { replace: true });
      });
  };

  const silentRefresh = useCallback(() => {
    console.log('🔍 silentRefresh called', { token, isAuthenticated, isInitialized });
    
    if (authConfig?.test === true) {
      console.log('Test mode. Skipping silent refresh.');
      return;
    }
    
    // If we have a stored token, use it instead of refreshing
    const storedToken = getStoredToken();
    if (storedToken && !token) {
      console.log('✅ Using stored token instead of refreshing');
      setToken(storedToken);
      setTokenHeader(storedToken);
      return;
    }
    
    // If we have a current token, try to refresh it
    if (token) {
      console.log('🔄 Attempting token refresh...');
      // Set the token header before making the refresh request
      setTokenHeader(token);
      refreshToken.mutate(undefined, {
        onSuccess: (data: t.TRefreshTokenResponse | undefined) => {
          // Handle both old and new response formats
          let user, token = '';
          if (data) {
            if ('data' in data && data.data && typeof data.data === 'object') {
              // New standardized response format
              user = (data.data as any).user;
              token = (data.data as any).token || '';
            } else if (typeof data === 'object') {
              // Old direct response format
              user = (data as any).user;
              token = (data as any).token || '';
            }
          }
          
          if (token) {
            console.log('✅ Token refresh successful');
            setUserContext({ token, isAuthenticated: true, user });
            refreshAttemptedRef.current = false; // Reset flag on successful refresh
          } else {
            console.log('❌ Token is not present. User is not authenticated.');
            if (authConfig?.test === true) {
              return;
            }
            // Clear invalid stored data and navigate to login
            clearStoredAuth();
            console.log('🚪 Navigating to login (no valid token)');
            refreshAttemptedRef.current = false; // Reset flag when navigating to login
            navigate('/login');
          }
        },
        onError: (error) => {
          console.log('❌ refreshToken mutation error:', error);
          if (authConfig?.test === true) {
            return;
          }
          // Clear invalid stored data and navigate to login
          clearStoredAuth();
          console.log('🚪 Navigating to login (refresh failed)');
          refreshAttemptedRef.current = false; // Reset flag when navigating to login
          navigate('/login');
        },
      });
    } else {
      // No token available, navigate to login
      console.log('🚪 No token available, navigating to login');
      navigate('/login');
    }
  }, [token, authConfig, refreshToken, setUserContext, navigate]);

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    console.log('🚀 Initializing auth state from localStorage');
    const storedToken = getStoredToken();
    const storedUser = getStoredUser();
    
    console.log('📦 Stored data:', { 
      hasStoredToken: !!storedToken, 
      hasStoredUser: !!storedUser,
      storedTokenLength: storedToken?.length 
    });
    
    // Restore authentication state from localStorage if available
    if (storedToken && storedUser) {
      console.log('✅ Restoring authentication state from localStorage');
      setToken(storedToken);
      setTokenHeader(storedToken);
      setUser(storedUser);
      setIsAuthenticated(true);
    } else {
      console.log('❌ No stored authentication data found');
      clearStoredAuth();
    }
    
    // Always mark as initialized, whether we have stored auth or not
    setIsInitialized(true);
    console.log('✅ Auth initialization complete');
  }, []);

  useEffect(() => {
    console.log('🔄 Auth state effect', { 
      token: !!token, 
      isAuthenticated, 
      isInitialized,
      userQueryData: !!userQuery.data,
      userQueryError: !!userQuery.isError,
      refreshAttempted: refreshAttemptedRef.current
    });
    
    if (userQuery.data) {
      console.log('✅ User query data received');
      setUser(userQuery.data);
      // Only set isAuthenticated to true if we have a token (user logged in)
      if (token) {
        console.log('✅ User is authenticated (has token)');
        setIsAuthenticated(true);
        

      } else {
        console.log('❌ User has data but no token - not authenticated');
        setIsAuthenticated(false);
      }
      refreshAttemptedRef.current = false; // Reset flag on successful auth
    } else if (userQuery.isError) {
      console.log('❌ User query error:', userQuery.error);
      doSetError((userQuery.error as Error).message);
      // Clear invalid stored data
      clearStoredAuth();
      setIsAuthenticated(false);
      // Try silent refresh when user query fails
      silentRefresh();
    }
    
    if (error != null && error && isAuthenticated) {
      doSetError(undefined);
    }
    
    // Only handle authentication state if we're initialized
    if (!isInitialized) {
      console.log('⏳ Not initialized yet, skipping auth state handling');
      return;
    }
    
    // Only handle authentication state changes, not initial setup
    if (isInitialized && !isAuthenticated && !token && !refreshAttemptedRef.current) {
      console.log('🚪 No token available, trying silent refresh before navigating to login');
      // Try silent refresh first, if it fails, navigate to login
      const storedToken = getStoredToken();
      if (storedToken) {
        console.log('🔄 Found stored token, attempting silent refresh');
        refreshAttemptedRef.current = true;
        silentRefresh();
      } else {
        console.log('🚪 No stored token, navigating to login');
        refreshAttemptedRef.current = false; // Reset flag when navigating to login
        navigate('/login');
      }
    }
  }, [
    token,
    isAuthenticated,
    isInitialized,
    userQuery.data,
    userQuery.isError,
    userQuery.error,
    error,
    navigate,
    setUserContext,
  ]);

  useEffect(() => {
    const handleTokenUpdate = (event) => {
      console.log('tokenUpdated event received event');
      const newToken = event.detail;
      setUserContext({
        token: newToken,
        isAuthenticated: true,
        user: user,
      });
    };

    window.addEventListener('tokenUpdated', handleTokenUpdate);

    return () => {
      window.removeEventListener('tokenUpdated', handleTokenUpdate);
    };
  }, [setUserContext, user]);

  // Make the provider update only when it should
  const memoedValue = useMemo(
    () => ({
      user,
      token,
      error,
      login,
      logout,
      setError,
      roles: {
        [SystemRoles.USER]: userRole,
        [SystemRoles.ADMIN]: adminRole,
      },
      isAuthenticated,
    }),

    [user, error, isAuthenticated, token, userRole, adminRole],
  );

  return <AuthContext.Provider value={memoedValue}>{children}</AuthContext.Provider>;
};

const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthContextProvider');
  }
  return context;
};

export { AuthContextProvider, useAuthContext, AuthContext };
