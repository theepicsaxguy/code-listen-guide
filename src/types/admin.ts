export interface AdminUser {
  id: string;
  email: string;
  name: string;
  role: "admin" | "user";
  created_at: string;
  last_login?: string;
  status: "active" | "suspended";
  credits: number;
}

export interface DashboardStats {
  total_users: number;
  active_jobs: number;
  total_audiobooks: number;
  revenue_today: number;
  revenue_month: number;
  storage_used_gb: number;
}

export interface AuditLog {
  id: string;
  admin_id: string;
  admin_email: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  details?: string;
  timestamp: string;
}

export interface Job {
  id: string;
  user_id: string;
  repo_url: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress: number;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface Payment {
  id: string;
  user_id: string;
  user_email: string;
  job_id?: string | null;
  amount: number;
  currency: string;
  status: "succeeded" | "pending" | "failed" | "refunded";
  payment_method?: string | null;
  stripe_payment_intent_id?: string | null;
  created_at: string;
  completed_at?: string | null;
}

export interface PaymentDetails extends Payment {
  user: {
    id: string;
    email: string;
    name: string;
  };
  job?: {
    id: string;
    repo_url: string;
    repo_name: string;
    status: string;
    depth_tier: string;
  } | null;
  amount_cents: number;
  stripe_charge_id?: string | null;
}

export interface PaymentStats {
  total_revenue: number;
  revenue_this_month: number;
  revenue_last_month: number;
  total_payments: number;
  status_counts: Record<string, number>;
  average_transaction: number;
  recent_transaction_count: number;
  revenue_chart_30_days: Array<{
    date: string;
    revenue: number;
  }>;
}

export interface ContentVersion {
  id: string;
  content_id: string;
  version: number;
  title: string;
  transcript?: string;
  audio_url?: string;
  status: "draft" | "published" | "archived";
  created_by: string;
  created_at: string;
  changes?: string;
}

export interface ContentSummary {
  id: string;
  title: string;
  status: string;
  description?: string;
  updated_at?: string;
}

export interface JobTrace {
  id: string;
  job_id: string;
  user_id: string;
  repo_url: string;
  status:
    | "queued"
    | "parsing"
    | "generating"
    | "rendering"
    | "completed"
    | "failed";
  started_at: string;
  completed_at?: string;
  error?: string;
  stages: JobStage[];
  tool_traces?: Record<string, Record<string, any>[]>;
}

export interface JobStage {
  name: string;
  status: "pending" | "running" | "completed" | "failed";
  started_at?: string;
  completed_at?: string;
  duration_ms?: number;
  error?: string;
  logs_url?: string;
}

export interface StageReplayResponse {
  success: boolean;
  job_id: string;
  stage: string;
  requested_at: string;
  message: string;
}

export interface SupportTicket {
  id: string;
  user_id: string;
  user_email: string;
  subject: string;
  status: "open" | "in_progress" | "waiting" | "resolved" | "closed";
  priority: "low" | "medium" | "high" | "urgent";
  category: "technical" | "billing" | "content" | "account" | "other";
  created_at: string;
  updated_at: string;
  assigned_to?: string;
  messages: TicketMessage[];
  context?: {
    job_id?: string;
    content_id?: string;
    payment_id?: string;
  };
}

export interface TicketMessage {
  id: string;
  ticket_id: string;
  author_id: string;
  author_name: string;
  author_type: "user" | "admin";
  content: string;
  created_at: string;
  attachments?: string[];
}

export interface CannedReply {
  id: string;
  title: string;
  content: string;
  category: string;
}
