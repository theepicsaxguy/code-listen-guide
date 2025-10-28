import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api';

export const useUser = () => {
  return useQuery({
    queryKey: ['user'],
    queryFn: () => apiClient.getMe(),
  });
};
