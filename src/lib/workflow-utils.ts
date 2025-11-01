import {
  WorkflowRevision,
  WorkflowStep,
  WorkflowWithSteps,
} from "@/lib/types/workflow";

const asRecord = (value: unknown): Record<string, unknown> =>
  typeof value === "object" && value !== null
    ? (value as Record<string, unknown>)
    : {};

const ensureRecord = (value: unknown): Record<string, unknown> =>
  asRecord(value);

const ensureArray = (value: unknown): unknown[] =>
  Array.isArray(value) ? value : [];

const ensureTools = (value: unknown): string[] => {
  if (Array.isArray(value)) {
    return value
      .map((entry) => (typeof entry === "string" ? entry.trim() : ""))
      .filter((entry) => entry.length > 0);
  }
  if (typeof value === "string") {
    return value
      .split(",")
      .map((entry) => entry.trim())
      .filter((entry) => entry.length > 0);
  }
  return [];
};

const readId = (value: unknown, fallback: string): string => {
  if (typeof value === "string" && value.length > 0) {
    return value;
  }
  if (typeof value === "number" && Number.isFinite(value)) {
    return String(value);
  }
  return fallback;
};

const readOptionalId = (value: unknown): string | null => {
  if (typeof value === "string" && value.length > 0) {
    return value;
  }
  if (typeof value === "number" && Number.isFinite(value)) {
    return String(value);
  }
  return null;
};

const readName = (value: unknown, fallback: string): string =>
  typeof value === "string" && value.trim().length > 0 ? value : fallback;

const readNumber = (value: unknown, fallback: number): number => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const readTimestampOrDefault = (value: unknown, fallback: string): string =>
  typeof value === "string" && value.length > 0 ? value : fallback;

const readTimestampOrNull = (value: unknown): string | null =>
  typeof value === "string" && value.length > 0 ? value : null;

const allowedModes = new Set<WorkflowStep["execution_mode"]>([
  "sequential",
  "concurrent",
  "conditional",
]);

export const normalizeWorkflowStep = (
  raw: unknown,
  revisionId: string,
): WorkflowStep => {
  const source = asRecord(raw);
  const modeValue = source["execution_mode"];
  const retrySource = asRecord(source["retry_policy"]);
  const stepConfig = ensureRecord(source["step_config"]);

  const maxRetries = readNumber(retrySource["max_retries"], NaN);
  const backoff =
    typeof retrySource["backoff"] === "string"
      ? (retrySource["backoff"] as string)
      : undefined;
  const retryPolicy =
    Number.isNaN(maxRetries) && !backoff
      ? null
      : {
          ...(Number.isNaN(maxRetries) ? {} : { max_retries: maxRetries }),
          ...(backoff ? { backoff } : {}),
        };

  return {
    id: readId(source["id"], ""),
    revision_id: readId(source["revision_id"], revisionId),
    step_order: readNumber(source["step_order"], 0),
    step_name: readName(source["step_name"], "Step"),
    agent_id: source["agent_id"]
      ? typeof source["agent_id"] === "string"
        ? (source["agent_id"] as string)
        : String(source["agent_id"])
      : null,
    agent_name:
      typeof source["agent_name"] === "string"
        ? (source["agent_name"] as string)
        : null,
    execution_mode:
      typeof modeValue === "string" &&
      allowedModes.has(modeValue as WorkflowStep["execution_mode"])
        ? (modeValue as WorkflowStep["execution_mode"])
        : "sequential",
    input_mapping: ensureRecord(source["input_mapping"]),
    output_mapping: ensureRecord(source["output_mapping"]),
    checkpoint_enabled: Boolean(source["checkpoint_enabled"]),
    retry_policy: retryPolicy,
    step_config: stepConfig,
    allowed_tools: ensureTools(source["allowed_tools"]),
  };
};

export const normalizeWorkflowRevision = (
  raw: unknown,
  workflowId: string,
): WorkflowRevision => {
  const source = asRecord(raw);
  const revisionId = readId(source["id"], workflowId);
  const metadata = ensureRecord(source["revision_metadata"]);
  const revisionMetadata = Object.keys(metadata).length > 0 ? metadata : null;
  const stepsSource = ensureArray(source["steps"]);

  return {
    id: revisionId,
    workflow_definition_id: readId(
      source["workflow_definition_id"],
      workflowId,
    ),
    version: readNumber(source["version"], 0),
    is_published: Boolean(source["is_published"]),
    revision_metadata: revisionMetadata,
    created_at: readTimestampOrDefault(
      source["created_at"],
      new Date(0).toISOString(),
    ),
    published_at: readTimestampOrNull(source["published_at"]),
    steps: stepsSource.map((step) => normalizeWorkflowStep(step, revisionId)),
  };
};

export const normalizeWorkflow = (raw: unknown): WorkflowWithSteps => {
  const source = asRecord(raw);
  const definition = source["definition"];

  if (definition) {
    const def = asRecord(definition);
    const workflowId = readId(def["id"], "");
    let revisionRaw = source["current_revision"] ?? source["revision"];
    if (!revisionRaw && Array.isArray(source["steps"])) {
      revisionRaw = { steps: source["steps"] };
    }

    return {
      id: workflowId,
      name: readName(def["name"], ""),
      description:
        typeof def["description"] === "string"
          ? (def["description"] as string)
          : null,
      current_revision_id: readOptionalId(def["current_revision_id"]),
      created_at: readTimestampOrDefault(
        def["created_at"],
        new Date(0).toISOString(),
      ),
      updated_at: readTimestampOrDefault(
        def["updated_at"],
        readTimestampOrDefault(def["created_at"], new Date(0).toISOString()),
      ),
      current_revision: revisionRaw
        ? normalizeWorkflowRevision(revisionRaw, workflowId)
        : null,
    };
  }

  const workflowId = readId(source["id"], "");
  let revisionRaw = source["current_revision"] ?? source["revision"];
  if (!revisionRaw && Array.isArray(source["steps"])) {
    revisionRaw = { steps: source["steps"] };
  }

  return {
    id: workflowId,
    name: readName(source["name"], ""),
    description:
      typeof source["description"] === "string"
        ? (source["description"] as string)
        : null,
    current_revision_id: readOptionalId(source["current_revision_id"]),
    created_at: readTimestampOrDefault(
      source["created_at"],
      new Date(0).toISOString(),
    ),
    updated_at: readTimestampOrDefault(
      source["updated_at"],
      readTimestampOrDefault(source["created_at"], new Date(0).toISOString()),
    ),
    current_revision: revisionRaw
      ? normalizeWorkflowRevision(revisionRaw, workflowId)
      : null,
  };
};

export const normalizeWorkflowList = (
  payload: unknown,
): WorkflowWithSteps[] => {
  if (Array.isArray(payload)) {
    return payload.map((item) => normalizeWorkflow(item));
  }
  const source = asRecord(payload);
  const collection = ensureArray(source["workflows"]);
  return collection.map((item) => normalizeWorkflow(item));
};

export const normalizeRevisionList = (
  payload: unknown,
  workflowId: string,
): WorkflowRevision[] => {
  if (Array.isArray(payload)) {
    return payload.map((item) => normalizeWorkflowRevision(item, workflowId));
  }
  const source = asRecord(payload);
  const collection = ensureArray(source["revisions"]);
  return collection.map((item) => normalizeWorkflowRevision(item, workflowId));
};
