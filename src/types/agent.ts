
export interface Checkpoint {
  step: string;
  state: Record<string, any>;
  created_at: string;
}

export interface JobUser {
  id: string;
  email: string;
  name: string;
}

export interface JobStage {
  name: string;
  status: "pending" | "running" | "completed" | "failed";
  started_at?: string;
  state?: Record<string, any>;
}

export interface AgentJob {
  id: string;
  user_email: string;
  user_name: string;
  repo_url: string;
  repo_name: string;
  repo_owner: string;
  git_ref: string;
  depth_tier: string;
  status: string; // This will need to be mapped to the frontend's ConversationStatus
  progress_percentage: number;
  current_stage: string;
  estimated_duration_minutes: number;
  estimated_chapters: number;
  price_paid_cents: number;
  llm_cost_cents: number;
  tts_cost_cents: number;
  created_at: string;
  updated_at: string;
  error_message?: string;
  checkpoint?: {
    step?: string;
    state?: Record<string, any>;
    created_at?: string;
  };
  checkpoints?: Checkpoint[]; // For detailed job view
  stages?: JobStage[]; // For detailed job view
  metadata?: Record<string, any>;
}

export interface AgentJobLog {
  timestamp: string;
  step: string;
  message: string;
  state?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface ListAgentJobsResponse {
  jobs: AgentJob[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface AgentStats {
  total_jobs: number;
  running_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  pending_jobs: number;
  recent_jobs_24h: number;
  avg_llm_cost_cents: number;
  avg_tts_cost_cents: number;
  total_checkpoints: number;
}
