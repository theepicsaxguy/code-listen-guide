import { useGetMeApiV1AuthMeGet } from '@/lib/api/generated';

export const useUser = () => {
  return useGetMeApiV1AuthMeGet();
};
