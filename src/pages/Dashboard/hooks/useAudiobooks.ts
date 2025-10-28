import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api';
import type { Job } from '../../../lib/types';

export const useAudiobooks = (params?: { status?: string; limit?: number; page?: number }) => {
  return useQuery({
    queryKey: ['audiobooks', params],
    queryFn: () => apiClient.getJobs(params),
  });
};

export const useAudiobook = (jobId: string | null) => {
  return useQuery({
    queryKey: ['audiobook', jobId],
    queryFn: () => {
      if (!jobId) throw new Error('Job ID is required');
      return apiClient.getJob(jobId);
    },
    enabled: !!jobId,
  });
};

export const useCreateAudiobook = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { repo_url: string; depth_tier: string; git_ref?: string }) =>
      apiClient.createJob(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audiobooks'] });
    },
  });
};

export const useDeleteAudiobook = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId: string) => apiClient.deleteJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audiobooks'] });
    },
  });
};

export const useAudiobookChapters = (jobId: string | null) => {
  return useQuery({
    queryKey: ['audiobook', jobId, 'chapters'],
    queryFn: async () => {
      if (!jobId) throw new Error('Job ID is required');
      const playerData = await apiClient.getPlayerData(jobId);
      return playerData;
    },
    enabled: !!jobId,
  });
};
