import { useQueryClient } from '@tanstack/react-query';
import {
  useListJobsApiV1JobsGet,
  useGetJobApiV1JobsJobIdGet,
  useCreateJobApiV1JobsPost,
  useDeleteJobApiV1JobsJobIdDelete,
  useGetAudiobookPlayerDataApiV1PlayerJobIdGet,
} from '@/lib/api/generated';

export const useAudiobooks = (params?: { status_filter?: string; limit?: number; offset?: number }) => {
  return useListJobsApiV1JobsGet(params ? {
    query: {
      status_filter: params.status_filter,
      limit: params.limit || 10,
      offset: params.offset || 0,
    },
  } : undefined);
};

export const useAudiobook = (jobId: string | null) => {
  return useGetJobApiV1JobsJobIdGet(jobId || '', {
    query: {
      enabled: !!jobId,
    },
  });
};

export const useCreateAudiobook = () => {
  const queryClient = useQueryClient();
  const mutation = useCreateJobApiV1JobsPost({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['listJobsApiV1JobsGet'] });
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
  const mutation = useDeleteJobApiV1JobsJobIdDelete({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['listJobsApiV1JobsGet'] });
      },
    },
  });

  return {
    ...mutation,
    mutateAsync: async (jobId: string) => {
      return mutation.mutateAsync(jobId);
    },
  };
};

export const useAudiobookChapters = (jobId: string | null) => {
  return useGetAudiobookPlayerDataApiV1PlayerJobIdGet(jobId || '', {
    query: {
      enabled: !!jobId,
    },
  });
};
