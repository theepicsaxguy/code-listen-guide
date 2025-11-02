import { useGetMe } from '@/lib/api/generated';

export const useUser = () => {
  return useGetMe();
};
