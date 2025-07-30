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
import { debounce } from 'lodash';
import { useRecoilState } from 'recoil';
import { useNavigate } from 'react-router-dom';
import { setTokenHeader, SystemRoles } from 'librechat-data-provider';
import type * as t from 'librechat-data-provider';
import {
  useGetRole,
  useGetUserQuery,
  useLoginUserMutation,
  useLogoutUserMutation,
  useRefreshTokenMutation,
} from '~/data-provider';
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
  const [token, setToken] = useState<string | undefined>(getStoredToken);
  const [error, setError] = useState<string | undefined>(undefined);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!getStoredToken());
  const [isInitialized, setIsInitialized] = useState<boolean>(false);
  const logoutRedirectRef = useRef<string | undefined>(undefined);

  const { data: userRole = null } = useGetRole(SystemRoles.USER, {
    enabled: !!(isAuthenticated && (user?.role ?? '')),
  });
  const { data: adminRole = null } = useGetRole(SystemRoles.ADMIN, {
    enabled: !!(isAuthenticated && user?.role === SystemRoles.ADMIN),
  });

  const navigate = useNavigate();

  const setUserContext = useMemo(
    () =>
      debounce((userContext: TUserContext) => {
        const { token, isAuthenticated, user, redirect } = userContext;
        
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

        if (finalRedirect.startsWith('http://') || finalRedirect.startsWith('https://')) {
          window.location.href = finalRedirect;
        } else {
          navigate(finalRedirect, { replace: true });
        }
      }, 50),
    [navigate, setUser],
  );
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
        if (!res.ok) {
          const error = await res.text();
          throw new Error(error);
        }
        return res.json();
      })
      .then((result) => {
        // Directly set user context here, do not call loginUser.mutate
        const { user, token, token_type } = result;
        setUserContext({
          token: token,
          isAuthenticated: true,
          user,
          redirect: '/c/new',
        });
        setError(undefined);
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
          const { user, token = '' } = data ?? {};
          if (token) {
            console.log('✅ Token refresh successful');
            setUserContext({ token, isAuthenticated: true, user });
          } else {
            console.log('❌ Token is not present. User is not authenticated.');
            if (authConfig?.test === true) {
              return;
            }
            // Clear invalid stored data and navigate to login
            clearStoredAuth();
            console.log('🚪 Navigating to login (no valid token)');
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
    
    if (storedToken && storedUser) {
      console.log('✅ Restoring authentication state from localStorage');
      // Restore authentication state from localStorage
      setToken(storedToken);
      setUser(storedUser);
      setIsAuthenticated(true);
      setTokenHeader(storedToken);
    } else {
      console.log('❌ No valid stored auth data found');
      // Clear any invalid stored data
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
      userQueryError: !!userQuery.isError
    });
    
    if (userQuery.data) {
      console.log('✅ User query data received');
      setUser(userQuery.data);
    } else if (userQuery.isError) {
      console.log('❌ User query error:', userQuery.error);
      doSetError((userQuery.error as Error).message);
      // Don't immediately navigate to login on user query error
      // Let the silentRefresh handle it
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
    if (isInitialized && !isAuthenticated && !token) {
      console.log('🚪 No token available, navigating to login');
      navigate('/login');
    }
  }, [
    token,
    isAuthenticated,
    isInitialized,
    userQuery.data,
    userQuery.isError,
    userQuery.error,
    error,
    setUser,
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
