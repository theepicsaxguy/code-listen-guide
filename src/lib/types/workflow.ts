/**
 * Workflow management types for dynamic workflow system
 */

export interface AgentRegistry {
  id: string;
  name: string;
  module_path: string;
  factory_function: string;
  description: string;
  config_schema: Record<string, unknown>;
  tools: string[];
  created_at: string;
  updated_at: string;
}

export interface ToolRegistry {
  id: string;
  name: string;
  module_path: string;
  function_name: string;
  description: string;
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
  created_at: string;
}

export interface WorkflowDefinition {
  id: string;
  name: string;
  description: string | null;
  current_revision_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorkflowRevision {
  id: string;
  workflow_definition_id: string;
  version: number;
  is_published: boolean;
  revision_metadata: Record<string, unknown> | null;
  created_at: string;
  published_at: string | null;
  steps: WorkflowStep[];
}

export interface WorkflowStep {
  id: string;
  revision_id: string;
  step_order: number;
  step_name: string;
  agent_id: string | null;
  agent_name?: string | null;
  execution_mode: "sequential" | "concurrent" | "conditional";
  input_mapping?: Record<string, unknown> | null;
  output_mapping?: Record<string, unknown> | null;
  checkpoint_enabled: boolean;
  retry_policy?: {
    max_retries?: number;
    backoff?: string;
  } | null;
  step_config?: Record<string, unknown> | null;
  allowed_tools?: string[] | null;
}

export interface WorkflowInstance {
  id: string;
  job_id: string;
  revision_id: string;
  current_step_id: string | null;
  instance_state: Record<string, unknown>;
  started_at: string | null;
  completed_at: string | null;
  status: "running" | "paused" | "completed" | "failed";
}

export interface WorkflowWithSteps {
  id: string;
  name: string;
  description: string | null;
  current_revision_id: string | null;
  created_at: string;
  updated_at: string;
  current_revision: WorkflowRevision | null;
}

export interface CreateWorkflowRevisionRequest {
  workflow_definition_id: string;
  revision_metadata: {
    author: string;
    notes: string;
    changelog?: string;
  };
  steps: Omit<WorkflowStep, "id" | "revision_id">[];
}

export interface PublishRevisionRequest {
  revision_id: string;
}

export interface ValidationResult {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface UpdateWorkflowStepRequest {
  step_name?: string;
  agent_id?: string | null;
  execution_mode?: "sequential" | "concurrent" | "conditional";
  input_mapping?: Record<string, unknown> | null;
  output_mapping?: Record<string, unknown> | null;
  checkpoint_enabled?: boolean;
  retry_policy?: {
    max_retries?: number;
    backoff?: string;
  } | null;
  step_config?: Record<string, unknown> | null;
  allowed_tools?: string[] | null;
}
