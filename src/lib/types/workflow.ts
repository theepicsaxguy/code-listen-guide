/**
 * Workflow management types for dynamic workflow system
 */

export interface AgentRegistry {
  id: string;
  name: string;
  module_path: string;
  factory_function: string;
  description: string;
  config_schema: Record<string, any>;
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
  input_schema: Record<string, any>;
  output_schema: Record<string, any>;
  created_at: string;
  description_version: string;
}

export interface WorkflowDefinition {
  id: string;
  name: string;
  description: string;
  current_revision_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorkflowRevision {
  id: string;
  workflow_definition_id: string;
  version: number;
  is_published: boolean;
  revision_metadata: {
    author?: string;
    notes?: string;
    changelog?: string;
  };
  created_at: string;
  published_at: string | null;
}

export interface WorkflowStep {
  id: string;
  revision_id: string;
  step_order: number;
  step_name: string;
  agent_id: string | null;
  execution_mode: 'sequential' | 'concurrent' | 'conditional';
  input_mapping: Record<string, any>;
  output_mapping: Record<string, any>;
  checkpoint_enabled: boolean;
  retry_policy: {
    max_retries?: number;
    backoff?: string;
  } | null;
  step_config: Record<string, any>;
}

export interface WorkflowInstance {
  id: string;
  job_id: string;
  revision_id: string;
  current_step_id: string | null;
  instance_state: Record<string, any>;
  started_at: string | null;
  completed_at: string | null;
  status: 'running' | 'paused' | 'completed' | 'failed';
}

export interface WorkflowWithSteps {
  definition: WorkflowDefinition;
  revision: WorkflowRevision;
  steps: WorkflowStep[];
}

export interface CreateWorkflowRevisionRequest {
  workflow_definition_id: string;
  revision_metadata: {
    author: string;
    notes: string;
    changelog?: string;
  };
  steps: Omit<WorkflowStep, 'id' | 'revision_id'>[];
}

export interface PublishRevisionRequest {
  revision_id: string;
}

export interface ValidationResult {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
}
