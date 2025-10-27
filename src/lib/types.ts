// Type definitions for the application

export interface User {
  id: string;
  email: string;
  name: string;
  subscription_tier: 'free' | 'professional' | 'team' | 'enterprise';
  subscription_status?: string;
  credits_remaining: number;
  created_at: string;
}

export interface Job {
  id: string;
  user_id: string;
  repo_url: string;
  repo_name: string;
  repo_owner: string;
  git_ref: string;
  repo_size_bytes?: number;
  file_count?: number;
  depth_tier: 'survey' | 'standard' | 'comprehensive';
  estimated_duration_minutes?: number;
  estimated_chapters?: number;
  status: 'pending' | 'analyzing' | 'scripting' | 'synthesizing' | 'post_processing' | 'completed' | 'failed';
  current_stage?: string;
  progress_percentage: number;
  error_message?: string;
  price_paid_cents?: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  updated_at: string;
  metadata?: any;
}

export interface Chapter {
  id: string;
  job_id: string;
  chapter_number: number;
  title: string;
  description?: string;
  files_covered: string[];
  topics_covered: string[];
  status: 'pending' | 'scripting' | 'synthesizing' | 'completed' | 'failed';
  script_text?: string;
  audio_url?: string;
  audio_duration_seconds?: number;
  audio_file_size_bytes?: number;
  start_timestamp_ms?: number;
  created_at: string;
  completed_at?: string;
  updated_at: string;
}

export interface Outline {
  id: string;
  job_id: string;
  outline_data: {
    chapters: OutlineChapter[];
    total_estimated_duration_minutes?: number;
    total_chapters?: number;
    depth_tier?: string;
  };
  user_approved: boolean;
  user_modifications?: any;
  created_at: string;
  approved_at?: string;
}

export interface OutlineChapter {
  number: number;
  title: string;
  description: string;
  estimated_duration_minutes: number;
  files_covered: string[];
  topics: string[];
  learning_objectives: string[];
}

export interface OutlineGenerateRequest {
  analysis_data: Record<string, unknown>;
}

export interface Deliverable {
  id: string;
  job_id: string;
  file_type: 'full_audiobook' | 'chapter_audio' | 'scripts_zip' | 'cover_image' | 'metadata_json' | 'outline_json' | 'code_map_json';
  file_url: string;
  file_size_bytes?: number;
  created_at: string;
}

export interface Payment {
  id: string;
  user_id: string;
  job_id: string;
  stripe_payment_intent_id?: string;
  amount_cents: number;
  currency: string;
  status: 'pending' | 'succeeded' | 'failed' | 'refunded';
  created_at: string;
  completed_at?: string;
}

export interface PlayerData {
  job_info: Job;
  chapters: Chapter[];
  audio_urls: string[];
  cover_url?: string;
  metadata: {
    audiobook_title: string;
    repo_url: string;
    total_duration_seconds: number;
    chapters: {
      number: number;
      title: string;
      start_time_seconds: number;
      duration_seconds: number;
    }[];
  };
}

export type DepthTier = 'survey' | 'standard' | 'comprehensive';

export interface DepthTierInfo {
  name: string;
  duration: string;
  price: number;
  features: string[];
  chapters: string;
}
