import { useEffect } from 'react';
import { useRecoilState } from 'recoil';
import { useAuthContext } from '~/hooks/AuthContext';
import StartupLayout from './Startup';
import store from '~/store';

export default function LoginLayout() {
  const { isAuthenticated } = useAuthContext();
  const [queriesEnabled, setQueriesEnabled] = useRecoilState<boolean>(store.queriesEnabled);
  
  useEffect(() => {
    // Ensure queries are enabled when not authenticated
    if (!isAuthenticated && !queriesEnabled) {
      console.log('🔧 Enabling queries for unauthenticated user');
      setQueriesEnabled(true);
    }
  }, [isAuthenticated, queriesEnabled, setQueriesEnabled]);
  
  return <StartupLayout isAuthenticated={isAuthenticated} />;
}
