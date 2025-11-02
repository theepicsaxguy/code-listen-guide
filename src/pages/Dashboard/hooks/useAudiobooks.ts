import { useQueryClient } from '@tanstack/react-query';
import {
  useListJobs,
  useGetJob,
  useCreateJob,
  useDeleteJob,
  useGetPlayerData,
} from '@/lib/api/generated';

export const useAudiobooks = (params?: { status_filter?: string; limit?: number; offset?: number }) => {
  return useListJobs(params ? {
    status_filter: params.status_filter,
    limit: params.limit || 10,
    offset: params.offset || 0,
  } : undefined, {});
};

export const useAudiobook = (jobId: string | null) => {
  return useGetJob(jobId || '', {
    query: {
      enabled: !!jobId,
    },
  });
};

export const useCreateAudiobook = () => {
  const queryClient = useQueryClient();
  const mutation = useCreateJob({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['listJobs'] });
      },
    },
  });

  return {
    ...mutation,
    mutateAsync: async (data: { repo_url: string; depth_tier: 'survey' | 'standard' | 'comprehensive'; git_ref?: string }) => {
      return mutation.mutateAsync({ data });
    },
  };
};

export const useDeleteAudiobook = () => {
  const queryClient = useQueryClient();
  const mutation = useDeleteJob({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['listJobs'] });
      },
    },
  });

  return {
    ...mutation,
    mutateAsync: async (jobId: string) => {
      return mutation.mutateAsync({ jobId });
    },
  };
};

export const useAudiobookChapters = (jobId: string | null) => {
  return useGetPlayerData(jobId || '', {
    query: {
      enabled: !!jobId,
    },
  });
};
