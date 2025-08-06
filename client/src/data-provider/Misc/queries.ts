import { useRecoilValue } from 'recoil';
import { QueryKeys, dataService } from 'librechat-data-provider';
import { useQuery } from '@tanstack/react-query';
import type { QueryObserverResult, UseQueryOptions } from '@tanstack/react-query';
import type t from 'librechat-data-provider';
import store from '~/store';

export const useGetBannerQuery = (
  config?: UseQueryOptions<t.TBannerResponse>,
): QueryObserverResult<t.TBannerResponse> => {
  const queriesEnabled = useRecoilValue<boolean>(store.queriesEnabled);
  return useQuery<t.TBannerResponse>([QueryKeys.banner], async () => {
    const response = await dataService.getBanner();
    // Handle standardized response format
    if (response && typeof response === 'object' && 'success' in response && 'data' in response) {
      if (response.success) {
        return response.data;
      } else {
        throw new Error(response.message || 'API request failed');
      }
    }
    // If not standardized format, return as is (for backward compatibility)
    return response;
  }, {
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    refetchOnMount: false,
    ...config,
    enabled: (config?.enabled ?? true) === true && queriesEnabled,
  });
};

export const useGetSearchEnabledQuery = (
  config?: UseQueryOptions<boolean>,
): QueryObserverResult<boolean> => {
  const queriesEnabled = useRecoilValue<boolean>(store.queriesEnabled);
  return useQuery<boolean>([QueryKeys.searchEnabled], async () => {
    const response = await dataService.getSearchEnabled();
    // Handle standardized response format
    if (response && typeof response === 'object' && 'success' in response && 'data' in response) {
      if (response.success) {
        return response.data;
      } else {
        throw new Error(response.message || 'API request failed');
      }
    }
    // If not standardized format, return as is (for backward compatibility)
    return response;
  }, {
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    refetchOnMount: false,
    ...config,
    enabled: (config?.enabled ?? true) === true && queriesEnabled,
  });
};
