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
import { useRecoilState, useSetRecoilState } from 'recoil';
import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
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
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const queryClient = useQueryClient();
  const setQueriesEnabled = useSetRecoilState<boolean>(store.queriesEnabled);
  const lastProcessedUserDataRef = useRef<any>(null);
  const authStateRef = useRef({ token, isAuthenticated, isInitialized });

  const { data: userRole = null } = useGetRole(SystemRoles.USER, {
    enabled: !!(isAuthenticated && (user?.role ?? '')),
  });
  const { data: adminRole = null } = useGetRole(SystemRoles.ADMIN, {
    enabled: !!(isAuthenticated && user?.role === SystemRoles.ADMIN),
  });

  const navigate = useNavigate();

  const setUserContext = useCallback((userContext: TUserContext) => {
    const { token, isAuthenticated, user, redirect } = userContext;
    
    // Only log if there's an actual change
    const hasChanged = authStateRef.current.token !== token || 
                      authStateRef.current.isAuthenticated !== isAuthenticated;
    
    if (hasChanged) {
      console.log('🔧 setUserContext called with:', { token: !!token, isAuthenticated, user: !!user, redirect });
    }
    
    // Update state
    setUser(user);
    setToken(token);
    setIsAuthenticated(isAuthenticated);
    
    // Update ref for change detection
    authStateRef.current = { token, isAuthenticated, isInitialized: authStateRef.current.isInitialized };
    
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
      // Reset processed user data ref for fresh processing on next login
      lastProcessedUserDataRef.current = null;
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
      // Reset processed user data ref for fresh processing on next login
      lastProcessedUserDataRef.current = null;
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

  const userQuery = useGetUserQuery({ 
    enabled: !!(token ?? '') && isAuthenticated,
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    refetchOnMount: false
  });

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
      
        return result.data;
      
      })
      .then((result) => {
        // Directly set user context here, do not call loginUser.mutate
        const { user, token, token_type } = result;
        console.log('🔧 Login successful, setting user context');
        console.log('🔧 Token received:', token ? `${token.substring(0, 20)}...` : 'null');
        
        // Update state immediately
        setUser(user);
        setToken(token);
        setIsAuthenticated(true);
        
        // Persist to localStorage
        setStoredToken(token);
        setStoredUser(user);
        
        // Set token header for API requests
        setTokenHeader(token || '');
        console.log('🔧 Token header set for API requests');
        
        // Reset refresh attempt flag to allow user query to run
        refreshAttemptedRef.current = false;
        
        // Enable queries and invalidate conversation cache
        setQueriesEnabled(true);
        
        // Add a small delay to ensure token header is set before queries run
        setTimeout(() => {
          console.log('🔧 Invalidating conversation cache after token set');
          queryClient.invalidateQueries({
            queryKey: [QueryKeys.allConversations],
            refetchPage: (_, index) => index === 0,
          });
          
          // Force refetch conversations immediately
          queryClient.refetchQueries({
            queryKey: [QueryKeys.allConversations],
            type: 'active',
          });
        }, 100);
        
        setError(undefined);
        
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
    
    // Prevent multiple simultaneous refresh attempts
    if (refreshAttemptedRef.current) {
      console.log('🔄 Refresh already attempted, skipping');
      return;
    }
    
    // Set a timeout to prevent infinite loops
    refreshTimeoutRef.current = setTimeout(() => {
      console.log('⏰ Refresh timeout reached, navigating to login');
      clearStoredAuth();
      navigate('/login');
    }, 10000); // 10 second timeout
    
    // If we have a stored token, use it instead of refreshing
    const storedToken = getStoredToken();
    if (storedToken && !token) {
      console.log('✅ Using stored token instead of refreshing');
      setToken(storedToken);
      setTokenHeader(storedToken);
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
        refreshTimeoutRef.current = null;
      }
      return;
    }
    
    // If we have a current token, try to refresh it
    if (token) {
      console.log('🔄 Attempting token refresh...');
      refreshAttemptedRef.current = true;
      // Set the token header before making the refresh request
      setTokenHeader(token);
      refreshToken.mutate(undefined, {
        onSuccess: (data: t.TRefreshTokenResponse | undefined) => {
          // Clear timeout on success
          if (refreshTimeoutRef.current) {
            clearTimeout(refreshTimeoutRef.current);
            refreshTimeoutRef.current = null;
          }
          
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
          // Clear timeout on error
          if (refreshTimeoutRef.current) {
            clearTimeout(refreshTimeoutRef.current);
            refreshTimeoutRef.current = null;
          }
          
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
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
        refreshTimeoutRef.current = null;
      }
      navigate('/login');
    }
  }, [token, isAuthenticated, isInitialized, authConfig, refreshToken, setUserContext, navigate, clearStoredAuth, setQueriesEnabled, queryClient]);

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

  // Consolidated auth state effect - only run when necessary
  useEffect(() => {
    const currentState = { token, isAuthenticated, isInitialized };
    const previousState = authStateRef.current;
    
    // Only log if there's a meaningful change
    const hasSignificantChange = 
      previousState.token !== token || 
      previousState.isAuthenticated !== isAuthenticated ||
      previousState.isInitialized !== isInitialized;
    
    if (hasSignificantChange) {
      console.log('🔄 Auth state effect', { 
        token: !!token, 
        isAuthenticated, 
        isInitialized,
        userQueryData: !!userQuery.data,
        userQueryError: !!userQuery.isError,
        refreshAttempted: refreshAttemptedRef.current
      });
    }
    
    // Update ref
    authStateRef.current = currentState;
    
    if (userQuery.data) {
      // Check if we've already processed this user data to prevent infinite loops
      if (lastProcessedUserDataRef.current === userQuery.data) {
        if (hasSignificantChange) {
          console.log('🔄 Skipping duplicate user data processing');
        }
        return;
      }
      
      if (hasSignificantChange) {
        console.log('✅ User query data received');
      }
      setUser(userQuery.data);
      lastProcessedUserDataRef.current = userQuery.data;
      
      // Only set isAuthenticated to true if we have a token (user logged in)
      if (token) {
        if (hasSignificantChange) {
          console.log('✅ User is authenticated (has token)');
        }
        setIsAuthenticated(true);
      } else {
        if (hasSignificantChange) {
          console.log('❌ User has data but no token - not authenticated');
        }
        setIsAuthenticated(false);
      }
      refreshAttemptedRef.current = false; // Reset flag on successful auth
    } else if (userQuery.isError) {
      console.log('❌ User query error:', userQuery.error);
      doSetError((userQuery.error as Error).message);
      // Clear invalid stored data
      clearStoredAuth();
      setIsAuthenticated(false);
      // Only try silent refresh if we haven't already attempted it
      if (!refreshAttemptedRef.current) {
        console.log('🔄 Attempting silent refresh due to user query error');
        refreshAttemptedRef.current = true;
        silentRefresh();
      } else {
        console.log('🚪 Already attempted refresh, navigating to login');
        navigate('/login');
      }
    }
    
    if (error != null && error && isAuthenticated) {
      doSetError(undefined);
    }
    
    // Only handle authentication state if we're initialized
    if (!isInitialized) {
      if (hasSignificantChange) {
        console.log('⏳ Not initialized yet, skipping auth state handling');
      }
      return;
    }
    
    // Only handle authentication state changes, not initial setup
    // Add guard to prevent infinite loop when user is already on login page
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
        // Set refreshAttempted to true to prevent infinite loop
        refreshAttemptedRef.current = true;
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
    silentRefresh,
    doSetError,
    clearStoredAuth,
    queryClient,
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

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, []);

  // Invalidate conversation cache when user becomes authenticated - only once
  useEffect(() => {
    if (isAuthenticated && isInitialized) {
      console.log('🔄 User authenticated, invalidating conversation cache');
      queryClient.invalidateQueries({
        queryKey: [QueryKeys.allConversations],
        refetchPage: (_, index) => index === 0,
      });
      
      // Force refetch conversations immediately
      queryClient.refetchQueries({
        queryKey: [QueryKeys.allConversations],
        type: 'active',
      });
    }
  }, [isAuthenticated, isInitialized, queryClient]);

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
