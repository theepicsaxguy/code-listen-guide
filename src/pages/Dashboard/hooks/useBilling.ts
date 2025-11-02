import { useGetPaymentHistoryApiV1PaymentsHistoryGet } from '@/lib/api/generated';

export const usePaymentHistory = () => {
  return useGetPaymentHistoryApiV1PaymentsHistoryGet();
};
