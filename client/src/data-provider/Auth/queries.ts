import { useRecoilValue } from 'recoil';
import { QueryKeys, dataService } from 'librechat-data-provider';
import { useQuery } from '@tanstack/react-query';
import type { QueryObserverResult, UseQueryOptions } from '@tanstack/react-query';
import type t from 'librechat-data-provider';
import store from '~/store';

export const useGetUserQuery = (
  config?: UseQueryOptions<t.TUser>,
): QueryObserverResult<t.TUser> => {
  const queriesEnabled = useRecoilValue<boolean>(store.queriesEnabled);
  return useQuery<t.TUser>([QueryKeys.user], async () => {
    const response = await dataService.getUser();
    // Handle standardized response format
    if (response && typeof response === 'object' && 'success' in response && 'data' in response) {
      const standardizedResponse = response as { success: boolean; data: any; message?: string };
      if (standardizedResponse.success) {
        // Extract user from data.user in standardized response
        return standardizedResponse.data.user;
      } else {
        throw new Error(standardizedResponse.message || 'API request failed');
      }
    }
    // If not standardized format, return as is (for backward compatibility)
    return response as t.TUser;
  }, {
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    refetchOnMount: false,
    retry: false,
    ...config,
    enabled: (config?.enabled ?? true) === true && queriesEnabled,
  });
};
