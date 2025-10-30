import { resolveApiBasePath } from './api-base-path';
import type { Job, OutlineGenerateRequest } from './types';

const API_BASE_PATH = resolveApiBasePath();

type JobResponsePayload = Omit<Job, 'progress_percentage'> & {
  progress_percentage: number | string;
};

export class ApiClient {
  private baseUrl: string;
  private _token: string | null = null; // Use _token for internal management

  constructor(baseUrl: string, initialToken: string | null = null) {
    this.baseUrl = baseUrl;
    this._token = initialToken;
  }

  setToken(token: string | null) {
    this._token = token;
  }

  getToken(): string | null {
    return this._token;
  }

  private async request<T = unknown>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this._token) {
      headers['Authorization'] = `Bearer ${this._token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
      credentials: 'include',  // Send cookies with requests
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      
      // Handle FastAPI validation errors (422)
      if (response.status === 422 && Array.isArray(error.detail)) {
        const fieldErrors = error.detail.map((err: any) => {
          const field = err.loc?.slice(1).join('.') || 'field';
          return `${field}: ${err.msg || err.ctx?.error || 'Invalid value'}`;
        }).join(', ');
        throw new Error(fieldErrors);
      }
      
      // Handle other error formats
      const errorMessage = typeof error.detail === 'string' 
        ? error.detail 
        : error.message || `HTTP ${response.status}`;
      throw new Error(errorMessage);
    }

    if (response.status === 204 || response.status === 205) {
      return undefined as T;
    }

    const contentLength = response.headers.get('Content-Length');
    if (contentLength !== null && Number.parseInt(contentLength, 10) === 0) {
      return undefined as T;
    }

    const text = await response.text();
    if (text.trim() === '') {
      return undefined as T;
    }

    try {
      return JSON.parse(text) as T;
    } catch {
      throw new Error('Invalid JSON response');
    }
  }

  private normalizeJob(job: JobResponsePayload): Job {
    const progress =
      typeof job.progress_percentage === 'string'
        ? Number.parseFloat(job.progress_percentage)
        : job.progress_percentage;

    return {
      ...job,
      progress_percentage: Number.isFinite(progress) ? progress : 0,
    };
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
    // Backend returns { access_token, refresh_token, token_type, expires_in, is_admin }
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
        return this.request<import('./types').User>('/auth/me');
      }
    
      // Admin endpoints (merged from api-client.ts)
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
    
      async getUserJobs(userId: string) {
        return this.request<{ jobs: Array<{
          id: string;
          repo_url: string;
          repo_name: string;
          status: string;
          depth_tier: string;
          price_paid_cents: number;
          created_at: string;
        }> }>(
          `/admin/users/${userId}/jobs`
        );
      }
    
      async updateUserCredits(userId: string, amount: number, operation: 'add' | 'subtract') {
        return this.request<{ success: boolean; new_balance: number }>(
          `/admin/users/${userId}/credits`,
          {
            method: 'POST',
            body: JSON.stringify({ amount, operation }),
          }
        );
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
    
      // Parse endpoints
      async parseRepository(params: {
        repo_url: string;
        git_ref?: string;
        max_file_size_kb?: number;
        enable_code_enrichment?: boolean;
        enable_formula_enrichment?: boolean;
        enable_table_extraction?: boolean;
        include_patterns?: string[] | null;
        exclude_patterns?: string[] | null;
      }) {
        return this.request<any>('/parse/repository', {
          method: 'POST',
          body: JSON.stringify(params),
        });
      }

      // Agent monitoring endpoints
      async getAgentStats() {
        return this.request<any>('/admin/agents/stats');
      }

      async getAgentJobs(status?: string) {
        const url = status ? `/admin/agents/jobs?status=${status}` : '/admin/agents/jobs';
        return this.request<{ jobs: any[]; total: number }>(url);
      }

      async getAgentJobDetails(jobId: string) {
        return this.request<any>(`/admin/agents/jobs/${jobId}`);
      }

      async getAgentJobLogs(jobId: string) {
        return this.request<{ logs: any[]; total: number }>(`/admin/agents/jobs/${jobId}/logs`);
      }

      async restartAgentJob(jobId: string) {
        return this.request<{ success: boolean }>(`/admin/agents/jobs/${jobId}/restart`, {
          method: 'POST',
        });
      }

      // Agent testing endpoints
      async testAgent(params: {
        agent_name: string;
        input_message: string;
        custom_instructions?: string;
        chapter_data?: Record<string, any>;
      }) {
        return this.request<{
          agent_name: string;
          input_message: string;
          output_message: string;
          messages: Array<{ role: string; content: string; timestamp: number }>;
          tools_called: Array<{ tool: string; arguments: any; timestamp: number }>;
          execution_time_seconds: number;
          error?: string;
        }>('/admin/agent-test/agent', {
          method: 'POST',
          body: JSON.stringify(params),
        });
      }

      async testWorkflow(params: {
        workflow_type: 'full' | 'analysis_only' | 'outline_only';
        repo_url: string;
        depth_tier?: string;
        git_ref?: string;
        custom_agent_instructions?: Record<string, string>;
      }) {
        return this.request<{
          workflow_id: string;
          stages: Array<{ name: string; status: string; output?: string }>;
          final_result: Record<string, any>;
          execution_time_seconds: number;
          error?: string;
        }>('/admin/agent-test/workflow', {
          method: 'POST',
          body: JSON.stringify(params),
        });
      }

      async listAvailableAgents() {
        return this.request<{
          agents: Array<{
            name: string;
            description: string;
            requires_input: boolean;
            requires_chapter_data?: boolean;
            tools: string[];
          }>;
        }>('/admin/agent-test/agents/list');
      }
    }
    
    export const apiClient = new ApiClient(API_BASE_PATH);
    
