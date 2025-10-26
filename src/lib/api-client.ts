const API_BASE_PATH = (() => {
  const configured = import.meta.env.VITE_API_BASE_PATH ?? '/api/v1';
  const trimmed = configured.trim();
  if (!trimmed.startsWith('/')) {
    throw new Error('VITE_API_BASE_PATH must be a path starting with "/"');
  }
  return trimmed.replace(/\/$/, '');
})();

export class ApiClient {
  private token: string | null = null;
  private readonly basePath: string;

  constructor(basePath: string = API_BASE_PATH) {
    this.basePath = basePath;
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('admin_token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('admin_token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('admin_token');
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };

    const response = await fetch(`${this.basePath}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      this.clearToken();
      throw new Error('Unauthorized - please login again');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || 'API request failed');
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  async login(email: string, password: string) {
    const data = await this.request<{ access_token: string; token_type: string }>(
      '/admin/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }
    );
    this.setToken(data.access_token);
    return data;
  }

  async getDashboardStats() {
    return this.request<import('@/types/admin').DashboardStats>('/admin/dashboard/stats');
  }

  async getUsers(page = 1, search?: string) {
    const params = new URLSearchParams({ page: page.toString() });
    if (search) params.append('search', search);
    return this.request<{ users: import('@/types/admin').AdminUser[]; total: number }>(
      `/admin/users?${params}`
    );
  }

  async getUser(userId: string) {
    return this.request<import('@/types/admin').AdminUser>(`/admin/users/${userId}`);
  }

  async updateUserStatus(userId: string, status: 'active' | 'suspended') {
    return this.request<{ success: boolean }>(`/admin/users/${userId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }

  async getAuditLogs(page = 1, filters?: Record<string, string>) {
    const params = new URLSearchParams({ page: page.toString(), ...filters });
    return this.request<{ logs: import('@/types/admin').AuditLog[]; total: number }>(
      `/admin/audit-logs?${params}`
    );
  }

  async getJobs(page = 1, status?: string) {
    const params = new URLSearchParams({ page: page.toString() });
    if (status) params.append('status', status);
    return this.request<{ jobs: import('@/types/admin').Job[]; total: number }>(
      `/admin/jobs?${params}`
    );
  }

  async getPayments(page = 1) {
    const params = new URLSearchParams({ page: page.toString() });
    return this.request<{ payments: import('@/types/admin').Payment[]; total: number }>(
      `/admin/payments?${params}`
    );
  }

  async getContentVersions(contentId: string) {
    return this.request<{ versions: import('@/types/admin').ContentVersion[] }>(
      `/admin/content/${contentId}/versions`
    );
  }

  async rollbackContent(contentId: string, versionId: string) {
    return this.request<{ success: boolean }>(`/admin/content/${contentId}/rollback/${versionId}`, {
      method: 'POST',
    });
  }

  async getContentList(page = 1, search?: string) {
    const params = new URLSearchParams({ page: page.toString() });
    if (search) params.append('search', search);
    return this.request<{ content: import('@/types/admin').ContentSummary[]; total: number }>(
      `/admin/content?${params}`
    );
  }

  async getJobTrace(jobId: string) {
    return this.request<import('@/types/admin').JobTrace>(`/admin/jobs/${jobId}/trace`);
  }

  async retryJobStage(jobId: string, stageName: string) {
    return this.request<{ success: boolean }>(`/admin/jobs/${jobId}/retry/${stageName}`, {
      method: 'POST',
    });
  }

  async getTickets(
    page = 1,
    filters?: { status?: string; priority?: string; category?: string }
  ) {
    const params = new URLSearchParams({ page: page.toString(), ...filters });
    return this.request<{ tickets: import('@/types/admin').SupportTicket[]; total: number }>(
      `/admin/support/tickets?${params}`
    );
  }

  async getTicket(ticketId: string) {
    return this.request<import('@/types/admin').SupportTicket>(
      `/admin/support/tickets/${ticketId}`
    );
  }

  async replyToTicket(ticketId: string, content: string) {
    return this.request<{ success: boolean }>(`/admin/support/tickets/${ticketId}/reply`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  }

  async updateTicketStatus(ticketId: string, status: string) {
    return this.request<{ success: boolean }>(`/admin/support/tickets/${ticketId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }

  async getCannedReplies() {
    return this.request<{ replies: import('@/types/admin').CannedReply[] }>(
      '/admin/support/canned-replies'
    );
  }
}

export const apiClient = new ApiClient();
