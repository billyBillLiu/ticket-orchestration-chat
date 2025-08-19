import { useRecoilValue } from 'recoil';
import { useGetStartupConfig } from '~/data-provider';
import store from '~/store';

export const useDefaultModel = () => {
  const { data: startupConfig, isLoading } = useGetStartupConfig();
  const queriesEnabled = useRecoilValue<boolean>(store.queriesEnabled);
  
  // Return the active model from startup config - no fallback, wait for backend
  return startupConfig?.activeModel;
};
