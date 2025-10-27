import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('./api-base-path', () => ({
  resolveApiBasePath: () => '/api/v1',
}));

import { ApiClient } from './api';

describe('ApiClient', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('returns undefined when deleting a job with an empty response body', async () => {
    const client = new ApiClient('https://example.com');
    const response = {
      ok: true,
      status: 204,
      headers: new Headers(),
      text: vi.fn().mockResolvedValue(''),
      json: vi.fn(),
    } as unknown as Response;
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(response);

    await expect(client.deleteJob('job-123')).resolves.toBeUndefined();
    expect(fetchSpy).toHaveBeenCalledWith('https://example.com/jobs/job-123', expect.objectContaining({ method: 'DELETE' }));
  });
});
