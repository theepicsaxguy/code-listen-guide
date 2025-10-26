// API Client for Backend Communication

const API_BASE_PATH = (() => {
  const configured = import.meta.env.VITE_API_BASE_PATH ?? '/api/v1';
  const trimmed = configured.trim();
  if (!trimmed.startsWith('/')) {
    throw new Error('VITE_API_BASE_PATH must be a path starting with "/"');
  }
  return trimmed.replace(/\/$/, '');
})();

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    if (typeof window !== 'undefined') {
      this.token = window.localStorage.getItem('auth_token');
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window === 'undefined') {
      return;
    }

    if (token) {
      window.localStorage.setItem('auth_token', token);
    } else {
      window.localStorage.removeItem('auth_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  async register(email: string, password: string, name: string) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });
  }

  async login(email: string, password: string) {
    // Backend expects OAuth2 form data, not JSON
    const formData = new URLSearchParams();
    formData.append('username', email); // OAuth2 uses 'username' field for email
    formData.append('password', password);

    const headers: HeadersInit = {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        ...headers,
      },
      body: formData.toString(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    const data = await response.json();
    // Backend returns { access_token, refresh_token, token_type, expires_in }
    this.setToken(data.access_token);

    // Fetch user data after login
    const user = await this.getMe();

    return { access_token: data.access_token, refresh_token: data.refresh_token, user };
  }

  async logout() {
    await this.request('/auth/logout', { method: 'POST' });
    this.setToken(null);
  }

  async refreshToken(refreshToken: string) {
    const data = await this.request<{ access_token: string; refresh_token: string; token_type: string; expires_in: number }>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async getMe() {
    return this.request('/auth/me');
  }

  // Job endpoints
  async createJob(data: {
    repo_url: string;
    depth_tier: string;
    git_ref?: string;
  }) {
    return this.request<{ job_id: string; estimated_cost: number; estimated_time: number }>('/jobs', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getJobs(params?: { status?: string; limit?: number; page?: number }) {
    // Backend expects 'offset' and 'status_filter', not 'page' and 'status'
    const backendParams: Record<string, string> = {};
    if (params?.status) {
      backendParams.status_filter = params.status;
    }
    if (params?.limit !== undefined) {
      backendParams.limit = String(params.limit);
    }
    if (params?.page !== undefined) {
      // Convert page to offset (page starts at 1, offset at 0)
      const limit = params.limit || 10;
      backendParams.offset = String((params.page - 1) * limit);
    }
    const query = new URLSearchParams(backendParams).toString();
    return this.request<{ jobs: any[]; total: number; page: number }>(`/jobs${query ? `?${query}` : ''}`);
  }

  async getJob(jobId: string) {
    return this.request<any>(`/jobs/${jobId}`);
  }

  async deleteJob(jobId: string) {
    return this.request(`/jobs/${jobId}`, { method: 'DELETE' });
  }

  async estimateJobCost(repoUrl: string, depthTier: string) {
    return this.request<{ estimated_cost_cents: number; estimated_time_minutes: number }>('/jobs/estimate', {
      method: 'POST',
      body: JSON.stringify({ repo_url: repoUrl, depth_tier: depthTier }),
    });
  }

  // Outline endpoints
  async generateOutline(jobId: string, data: { repo_url: string; depth_tier: string }) {
    return this.request(`/jobs/${jobId}/outline`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateOutline(jobId: string, outlineId: string, data: any) {
    // Backend expects outline data in request body, not outlineId in URL path
    return this.request(`/jobs/${jobId}/outline`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async approveOutline(jobId: string, outlineId: string) {
    // Backend expects outline_id in request body, not in URL path
    return this.request(`/jobs/${jobId}/outline/approve`, {
      method: 'POST',
      body: JSON.stringify({ outline_id: outlineId }),
    });
  }

  // Payment endpoints
  async createPaymentIntent(jobId: string, amount: number) {
    return this.request('/payments/create-intent', {
      method: 'POST',
      body: JSON.stringify({ job_id: jobId, amount_cents: amount }),
    });
  }

  async getPaymentHistory() {
    return this.request('/payments/history');
  }

  // Player endpoints (public)
  async getPlayerData(jobId: string) {
    return this.request(`/player/${jobId}`);
  }

  async getDownloadUrl(jobId: string, deliverableType: string) {
    // Backend route is under /player prefix, not /jobs
    return this.request(`/player/${jobId}/download/${deliverableType}`);
  }
}

export const apiClient = new ApiClient(API_BASE_PATH);
