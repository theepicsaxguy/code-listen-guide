import { useGetPaymentHistory } from '@/lib/api/generated';

export const usePaymentHistory = () => {
  return useGetPaymentHistory();
};
