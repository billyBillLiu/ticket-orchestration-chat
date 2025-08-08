import { useEffect, useState, useMemo, useRef } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import type { TStartupConfig } from 'librechat-data-provider';
import { useGetStartupConfig } from '~/data-provider';
import AuthLayout from '~/components/Auth/AuthLayout';
import { TranslationKeys, useLocalize } from '~/hooks';

const headerMap: Record<string, TranslationKeys> = {
  '/login': 'com_auth_welcome_back',
  '/register': 'com_auth_create_account',
  '/forgot-password': 'com_auth_reset_password',
  '/reset-password': 'com_auth_reset_password',
  '/login/2fa': 'com_auth_verify_your_identity',
};

export default function StartupLayout({ isAuthenticated }: { isAuthenticated?: boolean }) {
  const [error, setError] = useState<TranslationKeys | null>(null);
  const [headerText, setHeaderText] = useState<TranslationKeys | null>(null);
  const [startupConfig, setStartupConfig] = useState<TStartupConfig | null>(null);
  const prevStartupConfigRef = useRef<TStartupConfig | null>(null);
  
  const {
    data,
    isFetching,
    error: startupConfigError,
  } = useGetStartupConfig({
    enabled: !isAuthenticated || startupConfig === null,
    staleTime: Infinity, // Cache indefinitely since config rarely changes
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    refetchOnMount: false,
  });
  
  const localize = useLocalize();
  const navigate = useNavigate();
  const location = useLocation();

  // Memoize the effect dependencies to prevent unnecessary re-runs
  const effectDependencies = useMemo(() => ({
    isAuthenticated,
    hasData: !!data,
    startupConfig: !!startupConfig,
    dataKeys: data ? Object.keys(data) : [],
    emailLoginEnabled: data?.emailLoginEnabled,
    registrationEnabled: data?.registrationEnabled
  }), [isAuthenticated, data, startupConfig]);

  useEffect(() => {
    const hasSignificantChange = 
      prevStartupConfigRef.current !== startupConfig ||
      effectDependencies.isAuthenticated !== isAuthenticated ||
      effectDependencies.hasData !== !!data;
    
    if (hasSignificantChange) {
      console.log('🔄 StartupLayout effect:', { 
        isAuthenticated, 
        hasData: !!data, 
        startupConfig: !!startupConfig 
      });
    }
    
    if (isAuthenticated) {
      navigate('/c/new', { replace: true });
    }
    
    if (data && data !== prevStartupConfigRef.current) {
      console.log('✅ Setting startup config:', data);
      console.log('🔧 Config data structure:', effectDependencies);
      
      // Check if data is the standardized response format
      if (data.success && data.data) {
        console.log('🔧 Extracting config from standardized response');
        setStartupConfig(data.data);
      } else {
        console.log('🔧 Using data directly (not standardized response)');
        setStartupConfig(data);
      }
      
      prevStartupConfigRef.current = data;
    }
  }, [isAuthenticated, navigate, data, effectDependencies]);

  useEffect(() => {
    document.title = startupConfig?.appTitle || 'LibreChat';
  }, [startupConfig?.appTitle]);

  useEffect(() => {
    setError(null);
    setHeaderText(null);
  }, [location.pathname]);

  const contextValue = useMemo(() => ({
    error,
    setError,
    headerText,
    setHeaderText,
    startupConfigError,
    startupConfig,
    isFetching,
  }), [error, setError, headerText, setHeaderText, startupConfigError, startupConfig, isFetching]);

  return (
    <AuthLayout
      header={headerText ? localize(headerText) : localize(headerMap[location.pathname])}
      isFetching={isFetching}
      startupConfig={startupConfig}
      startupConfigError={startupConfigError}
      pathname={location.pathname}
      error={error}
    >
      <Outlet context={contextValue} />
    </AuthLayout>
  );
}
