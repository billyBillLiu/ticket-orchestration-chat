import { useRecoilValue } from 'recoil';
import { useGetStartupConfig } from '~/data-provider';
import store from '~/store';

export const useDefaultModel = () => {
  const { data: startupConfig } = useGetStartupConfig();
  const queriesEnabled = useRecoilValue<boolean>(store.queriesEnabled);
  
  // Return the default model from startup config, or fallback to a default value
  return startupConfig?.defaultModel || 'deepseek-r1:8b';
};
