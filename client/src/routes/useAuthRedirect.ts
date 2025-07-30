import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '~/hooks';

export default function useAuthRedirect() {
  const { user, isAuthenticated } = useAuthContext();
  const navigate = useNavigate();
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);

  useEffect(() => {
    // Give the auth system time to initialize
    const timeout = setTimeout(() => {
      setHasCheckedAuth(true);
      if (!isAuthenticated) {
        console.log('🚪 useAuthRedirect: Not authenticated, redirecting to login');
        navigate('/login', { replace: true });
      }
    }, 1000); // Increased timeout to allow for auth initialization

    return () => {
      clearTimeout(timeout);
    };
  }, [isAuthenticated, navigate]);

  return {
    user,
    isAuthenticated: hasCheckedAuth ? isAuthenticated : true, // Don't show as unauthenticated during initialization
  };
}
