import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api';

export const usePaymentHistory = () => {
  return useQuery({
    queryKey: ['payments', 'history'],
    queryFn: () => apiClient.getPaymentHistory(),
  });
};
