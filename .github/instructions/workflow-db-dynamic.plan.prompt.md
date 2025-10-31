---
name: workflow-db-dynamic
description: Comprehensive plan to migrate hardcoded Microsoft Agent Framework workflows to dynamic, DB-driven workflow definitions with hot-reload support, safe rollback, and runtime modification without backend restarts.
---

# DB-driven Workflows Migration Plan

**Last Updated:** October 31, 2025  
**Status:** Analysis Complete, Ready for Implementation

## Executive Summary

This plan transforms the current hardcoded `AudiobookWorkflow` class and inline agent compositions into a fully dynamic, database-driven workflow system. The migration enables runtime workflow editing, versioning, hot-reload, and safe rollback while preserving all existing checkpoint/resume capabilities and maintaining backward compatibility.

**Current State:**
- Workflows hardcoded in `backend/workflows/audiobook_workflow.py` (AudiobookWorkflow class)
- Agent orchestration embedded in Python code (SequentialBuilder/ConcurrentBuilder)
- 5 agent factories: analyzer, outline, script, audio, postprocess
- PostgreSQL checkpointing via `PostgresCheckpointStorage` (fully functional)
- In-process execution via FastAPI BackgroundTasks + asyncio.run
- Redis WebSocket pub/sub for real-time job updates

**Target State:**
- Workflow definitions stored as immutable, versioned revisions in PostgreSQL
- Dynamic workflow loading and validation via Workflow Manager service
- Hot-reload on publish via Postgres LISTEN/NOTIFY or Redis pub/sub
- Admin API for workflow CRUD, validation, and publishing
- Running instances locked to their revision (no mid-flight changes)
- Comprehensive telemetry, canary rollouts, and circuit breakers

---

## Objective

Move hardcoded workflow compositions (AudiobookWorkflow and inline builder code) into declarative workflow revisions stored in the database so workflows and agent configurations can be edited and published at runtime without restarting the backend. Keep legacy behavior as a fallback during rollout.

---

## Current Architecture Analysis

### Workflow Locations

**Primary Workflow:**
- **File:** `backend/workflows/audiobook_workflow.py`
- **Class:** `AudiobookWorkflow`
- **Role:** Main orchestrator for audiobook generation (analysis → outline → approval → scripting → audio → post-processing)
- **Key Methods:**
  - `execute()`: Runs initial analysis and outline stages, pauses at approval
  - `continue_after_approval()`: Resumes after outline approval, runs scripting → audio → post-processing
  - `cancel()`: Marks job as cancelled
- **Call Sites:**
  - `backend/tasks/audiobook_tasks.py::start_audiobook_workflow` (via `_create_workflow`)
  - `backend/tasks/audiobook_tasks.py::resume_audiobook_workflow` (via `_create_workflow`)

**Admin Test Endpoints:**
- **File:** `backend/api/routes/admin_routes/agent_test.py`
- **Endpoint:** `POST /api/v1/admin/agent-test/workflow`
- **Function:** `test_workflow`
- **Role:** Admin workflow builder for testing (analysis_only, outline_only, full)

### Task Entrypoints

**File:** `backend/tasks/audiobook_tasks.py`

**Functions:**
1. `_run_coroutine(coro)`: Executes coroutine in new event loop via `asyncio.run()`
2. `start_audiobook_workflow`: Calls `_run_coroutine(_start_audiobook_workflow)`, invokes `AudiobookWorkflow.execute()`
   - Called from: `backend/api/routes/jobs.py` (line 137, background task), `backend/api/routes/payments.py` (line 259, webhook handler)
3. `resume_audiobook_workflow`: Calls `_run_coroutine(_resume_audiobook_workflow)`, invokes `AudiobookWorkflow.continue_after_approval()`
   - Called from: `backend/api/routes/outlines.py` (line 142, background task after approval)

### Agent Factories

| Agent | File | Factory Function | Tools | DB/External Services |
|-------|------|------------------|-------|---------------------|
| **Analyzer** | `backend/agents/analyzer_agent.py` | `analyzer_agent(settings)` | `_ai_clone_repo`, `_ai_list_files`, `_ai_parse_repository` | Git clone, chonkie pipeline |
| **Outline** | `backend/agents/outline_agent.py` | `outline_agent(settings)` | None (response_format only) | None |
| **Script** | `backend/agents/script_agent.py` | `script_agent(settings, chapter_ctx)` | `_ai_save_script` → `save_chapter_script` | **DB WRITE: Chapter table** |
| **Audio** | `backend/agents/audio_agent.py` | `audio_agent(settings)` | `_ai_tts` → `synthesize_speech`, `_ai_upload` → `upload_to_s3` | **OpenAI TTS API, AWS S3** |
| **Postprocess** | `backend/agents/postprocess_agent.py` | `postprocess_agent(settings)` | `_ai_concat` → `concat_audio_with_chapters`, `_ai_upload` → `upload_to_s3` | **AWS S3** |

### Checkpointing Implementation

**File:** `backend/utils/checkpointing.py`

- **Class:** `PostgresCheckpointStorage` (implements `agent_framework.CheckpointStorage`)
- **Methods:**
  - `save_checkpoint`: Saves WorkflowCheckpoint to DB via `workflow_checkpoints` table
  - `load_checkpoint`: Loads checkpoint by ID
  - `list_checkpoints`: Returns all checkpoints for workflow_id
  - `delete_checkpoint`: Removes checkpoint by ID
- **Usage:**
  - `backend/workflows/audiobook_workflow.py::__init__`: `self.checkpoints = PostgresCheckpointStorage(workflow_id=job_id)`
  - Lines 113, 138: `.with_checkpointing(self.checkpoints)` for audio and post-processing workflows
- **Helper Functions:**
  - `save_checkpoint(workflow_id, step_id, state, metadata, thread_state, session)`
  - `load_checkpoint`, `list_checkpoints`, `list_checkpoint_ids`, `delete_checkpoint`

### Database Models

| Model | File | Table | Key Fields |
|-------|------|-------|------------|
| **Job** | `backend/models/job.py` | `jobs` | id (UUID), user_id, repo_url, repo_name, repo_owner, git_ref, depth_tier, status, current_stage, progress_percentage, estimated_duration_minutes, estimated_chapters, price_paid_cents, llm_cost_cents, tts_cost_cents, created_at, started_at, completed_at, updated_at, error_message, metadata_json (JSONB) |
| **Workflow Checkpoint** | `backend/models/workflow_checkpoint.py` | `workflow_checkpoints` | id (String PK), workflow_id (String, indexed), step_id (String, indexed), state (JSON), created_at (DateTime) |
| **Outline** | `backend/models/outline.py` | `outlines` | id (UUID), job_id (UUID, unique FK to jobs), outline_data (JSONB), user_approved (Boolean), user_modifications (JSONB), created_at, approved_at |
| **Chapter** | `backend/models/chapter.py` | `chapters` | id (UUID), job_id (UUID FK), chapter_number (Integer), title, description, files_covered (ARRAY Text), topics_covered (ARRAY Text), status, script_text, audio_url, audio_duration_seconds, audio_file_size_bytes, start_timestamp_ms, created_at, completed_at, updated_at. **Constraint:** UNIQUE(job_id, chapter_number) |
| **Deliverable** | `backend/models/deliverable.py` | `deliverables` | id (UUID), job_id (UUID FK), file_type (String: full_audiobook, chapter_audio, scripts_zip, etc.), file_url, file_size_bytes, created_at |

### Runtime Constraints

- **Workflow Execution:** In-process within FastAPI workers via background tasks (BackgroundTasks from FastAPI)
- **Background Tasks Module:** `backend/tasks/audiobook_tasks.py` wraps workflows with `asyncio.run()` for sync-to-async bridge
- **External Workers:** None (no Celery, no external queue)
- **WebSocket:** Enabled via `backend/api/ws.py::WebSocketManager`, uses Redis pub/sub, endpoint `/ws/jobs/{job_id}` for real-time job progress updates
- **Hardcoded Workflow Definitions:**
  - `backend/workflows/audiobook_workflow.py`: AudiobookWorkflow class with hardcoded `execute()` and `continue_after_approval()` methods
  - Agent sequence: SequentialBuilder for analyzer→outliner, ConcurrentBuilder for script agents
  - Batch size for audio: hardcoded `batch_size=5`

---

## Key Ideas

- Store workflow definitions as immutable revisions (JSONB) tied to a workflow identity. Each revision contains a sequence of steps, agent references, agent configuration overrides, batching/concurrency hints, and optional transition rules.
- Implement a Workflow Manager service that loads published revisions, validates them (JSON Schema), maps them to agent_framework builder calls (SequentialBuilder/ConcurrentBuilder/WorkflowBuilder) and exposes an in-memory registry keyed by `workflow_id` and `revision_id`.
- Use a notification mechanism to hot-reload published revisions: Postgres LISTEN/NOTIFY is recommended for single-DB deployments; Redis pub/sub is an option for multi-host scaling. The registry must apply revisions atomically and preserve running instances bound to their original revision.
- Use the existing `PostgresCheckpointStorage` (backend/utils/checkpointing.py) for checkpointing; extend checkpoint records to reference `workflow_instance_id` and `step_id`.
- Admin UI / API to author, validate (dry-run), and publish revisions. Publishing sets `workflow_definitions.current_revision_id` inside a DB transaction and emits a notification.

---

### Schema Tables

#### 1. `workflow_definitions`
Core workflow identity and versioning.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique workflow identifier |
| name | VARCHAR(255) | UNIQUE NOT NULL | Workflow name (e.g., 'audiobook_generation') |
| description | TEXT | | Human-readable description |
| current_revision_id | UUID | FK → workflow_revisions.id | Currently published revision |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

#### 2. `workflow_revisions`
Immutable workflow versions with complete configuration.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique revision identifier |
| workflow_definition_id | UUID | FK → workflow_definitions.id, NOT NULL | Parent workflow |
| version | INTEGER | NOT NULL | Auto-increment per workflow |
| is_published | BOOLEAN | DEFAULT FALSE | Published flag (immutable once TRUE) |
| revision_metadata | JSONB | | Author, notes, changelog |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| published_at | TIMESTAMP | | Publication timestamp |

**Constraints:** `UNIQUE(workflow_definition_id, version)`

#### 3. `workflow_steps`
Individual steps within a workflow revision.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique step identifier |
| revision_id | UUID | FK → workflow_revisions.id, NOT NULL | Parent revision |
| step_order | INTEGER | NOT NULL | Execution order (0-indexed) |
| step_name | VARCHAR(255) | NOT NULL | Step name (e.g., 'analysis', 'outline') |
| agent_id | UUID | FK → agents_registry.id, nullable | Agent to execute (null for custom executors) |
| execution_mode | VARCHAR(50) | NOT NULL | 'sequential', 'concurrent', 'conditional' |
| input_mapping | JSONB | | How to map prior outputs to inputs |
| output_mapping | JSONB | | How to map step outputs downstream |
| checkpoint_enabled | BOOLEAN | DEFAULT TRUE | Enable checkpointing for this step |
| retry_policy | JSONB | | max_retries, backoff strategy |
| step_config | JSONB | | Custom parameters (batch_size, etc.) |

**Constraints:** `UNIQUE(revision_id, step_order)`

#### 4. `agents_registry`
Registry of available agents and their factory functions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique agent identifier |
| name | VARCHAR(255) | UNIQUE NOT NULL | Agent name (e.g., 'analyzer_agent') |
| module_path | VARCHAR(500) | NOT NULL | Python module path (e.g., 'backend.agents.analyzer_agent') |
| factory_function | VARCHAR(255) | NOT NULL | Factory function name (e.g., 'analyzer_agent') |
| description | TEXT | | Agent purpose |
| config_schema | JSONB | | Expected inputs/outputs schema |
| tools | JSONB | | Array of tool names |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

#### 5. `tools_registry`
Registry of available tools for agents.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique tool identifier |
| name | VARCHAR(255) | UNIQUE NOT NULL | Tool name (e.g., 'clone_repository') |
| module_path | VARCHAR(500) | NOT NULL | Python module path |
| function_name | VARCHAR(255) | NOT NULL | Function name |
| description | TEXT | | Tool purpose |
| input_schema | JSONB | | Input parameters schema |
| output_schema | JSONB | | Output schema |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |

#### 6. `workflow_instances`
Runtime execution tracking for workflow runs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique instance identifier (same as job.id) |
| job_id | UUID | FK → jobs.id, NOT NULL | Associated job |
| revision_id | UUID | FK → workflow_revisions.id, NOT NULL | Locked revision |
| current_step_id | UUID | FK → workflow_steps.id, nullable | Current executing step |
| instance_state | JSONB | | Runtime state, outputs from completed steps |
| started_at | TIMESTAMP | | Execution start time |
| completed_at | TIMESTAMP | | Execution completion time |
| status | VARCHAR(50) | NOT NULL | 'running', 'paused', 'completed', 'failed' |

**Compatibility Notes:**
- `workflow_instances.id` maps to `workflow_checkpoints.workflow_id` (existing table preserved)
- Existing checkpoints continue working with extended metadata

---

## Runtime Architecture

### Workflow Manager Service

**Location:** `backend/services/workflow_manager.py`

**Responsibilities:**
- Load published revisions from database
- Validate `definition_json` against JSON Schema
- Compose builder templates (not live instances) mapping to agent factories
- Maintain in-memory registry of workflows
- Expose API to instantiate workflow instances by `revision_id` or workflow name

**Key Methods:**
```python
class WorkflowManager:
    def load_revision(self, revision_id: UUID) -> WorkflowRevision
    def get_current_revision(self, workflow_name: str) -> WorkflowRevision
    def validate_revision(self, revision: WorkflowRevision) -> ValidationResult
    def build_workflow(self, revision_id: UUID, job_id: UUID) -> WorkflowBuilder
    def reload_registry(self) -> None  # Called on notification
```

### Notification Watcher

**Option A: Postgres LISTEN/NOTIFY** (Recommended for single-DB deployments)
- Listen on channel `workflow_revision_published`
- Payload: `{"revision_id": "uuid", "workflow_name": "audiobook_generation"}`
- Transactional: notification only fires on commit
- Single-process or leader-election for multi-worker setups

**Option B: Redis Pub/Sub** (For multi-host scaling)
- Channel: `workflows:published`
- Same payload format as Option A
- Already used by WebSocket manager (`backend/api/ws.py`)
- Works across multiple backend instances

**Implementation:**
```python
async def watch_workflow_updates():
    async with db_connection.cursor() as cursor:
        await cursor.execute("LISTEN workflow_revision_published")
        async for notify in cursor:
            payload = json.loads(notify.payload)
            await workflow_manager.reload_registry()
```

### Runner / Instance Execution

**Location:** `backend/tasks/runner.py` (refactor of existing `audiobook_tasks.py`)

**Workflow:**
1. Job creation triggers workflow start
2. Runner asks Workflow Manager for current revision
3. Workflow Manager instantiates builder with agent factories
4. Runner executes workflow with checkpointing
5. Instance binds to `revision_id` (immutable during execution)
6. Checkpoints include `workflow_instance_id` + `step_id`

**Key Functions:**
```python
async def start_workflow_instance(job_id: UUID, workflow_name: str = "audiobook_generation"):
    revision = workflow_manager.get_current_revision(workflow_name)
    instance = create_workflow_instance(job_id, revision.id)
    workflow = workflow_manager.build_workflow(revision.id, job_id)
    
    async for event in workflow.run_stream(input_data):
        # Handle events, update instance state
        pass
```

### Admin API

**Location:** `backend/api/routes/admin_workflows.py`

**Endpoints:**
- `GET /api/v1/admin/workflows` - List all workflow definitions
- `POST /api/v1/admin/workflows` - Create new workflow definition
- `GET /api/v1/admin/workflows/{id}/revisions` - List revisions
- `POST /api/v1/admin/workflows/{id}/revisions` - Create new revision
- `POST /api/v1/admin/workflows/{id}/revisions/{revision_id}/validate` - Dry-run validation
- `POST /api/v1/admin/workflows/{id}/revisions/{revision_id}/publish` - Publish revision
- `GET /api/v1/admin/agents/registry` - List available agents
- `GET /api/v1/admin/tools/registry` - List available tools

**Publish Flow:**
```python
@router.post("/{workflow_id}/revisions/{revision_id}/publish")
async def publish_revision(workflow_id: UUID, revision_id: UUID, db: Session = Depends(get_db)):
    # 1. Validate revision (dry-run)
    validation = await workflow_manager.validate_revision(revision_id)
    if not validation.is_valid:
        raise HTTPException(400, detail=validation.errors)
    
    # 2. Transactionally update current_revision_id and mark published
    with db.begin():
        revision = db.query(WorkflowRevision).get(revision_id)
        revision.is_published = True
        revision.published_at = datetime.utcnow()
        
        workflow_def = db.query(WorkflowDefinition).get(workflow_id)
        workflow_def.current_revision_id = revision_id
        workflow_def.updated_at = datetime.utcnow()
        
        # 3. Emit notification (Postgres NOTIFY or Redis publish)
        await db.execute(
            "SELECT pg_notify('workflow_revision_published', :payload)",
            {"payload": json.dumps({"revision_id": str(revision_id), "workflow_name": workflow_def.name})}
        )
```

---

## Safety, Validation & Rollout

### Validation Strategy

1. **JSON Schema Validation:**
   - Validate `revision_metadata`, `step_config`, `input_mapping`, `output_mapping` against schemas
   - Ensure all agent_ids exist in `agents_registry`
   - Check for circular dependencies in step graph

2. **Dry-Run Mode:**
   - Attempt to instantiate builders with test/mocked agents
   - Validate that agent factories are importable and callable
   - Check tool availability for each agent

3. **Pre-Publish Checks:**
   - No duplicate `step_order` within revision
   - At least one step with `step_order = 0` (start step)
   - All conditional edges have valid conditions
   - All concurrent steps have compatible input types

### Immutability & Versioning

- **Published revisions are immutable:** Once `is_published = TRUE`, no edits allowed
- **Edits create new revision:** Copy existing revision, increment version, create new record
- **Running instances complete under original revision:** No mid-flight version changes
- **Optional migration:** Admin can restart instances from last checkpoint on new revision

### Transactional Publish

```sql
BEGIN;
  UPDATE workflow_revisions SET is_published = TRUE, published_at = NOW() WHERE id = :revision_id;
  UPDATE workflow_definitions SET current_revision_id = :revision_id, updated_at = NOW() WHERE id = :workflow_id;
  SELECT pg_notify('workflow_revision_published', :payload);
COMMIT;
```

### Rollout Strategy

1. **Canary Rollout:**
   - Feature flag in `workflow_instances`: `canary_percentage` (0-100)
   - Route X% of new jobs to new revision, remainder to old/hardcoded
   - Monitor failure rates, LLM costs, execution times

2. **Circuit Breaker:**
   - If >10% of jobs fail on new revision within 1 hour, auto-pause
   - Admin notification sent
   - Auto-rollback to previous `current_revision_id`

3. **Drain vs. Force Restart:**
   - **Drain:** New jobs use new revision, running jobs complete on old revision
   - **Force Restart:** Admin triggers restart from last checkpoint on new revision

### Logging & Telemetry

- Emit OpenTelemetry spans for each workflow step
- Track LLM/TTS usage per `workflow_instance_id`
- Log revision_id in all workflow-related logs
- Dashboard: show active instances by revision, failure rates, cost per revision

---

## Migration Sequence

### Step 1: Create DB Schema and Models

**Actions:**
- Add Alembic migration for 6 new tables
- Create SQLAlchemy models in `backend/models/`
- Run migration: `alembic upgrade head`

**Affected Files:**
- `backend/db/migrations/versions/YYYYMMDD_add_workflow_schema.py` (new)
- `backend/models/workflow_definition.py` (new)
- `backend/models/workflow_revision.py` (new)
- `backend/models/workflow_step.py` (new)
- `backend/models/agent_registry.py` (new)
- `backend/models/tool_registry.py` (new)
- `backend/models/workflow_instance.py` (new)

**Estimated Effort:** 1 day

### Step 2: Seed Registry with Existing Agents and Tools

**Actions:**
- Create seed script: `backend/scripts/seed_workflow_registry.py`
- Populate `agents_registry` with 5 agents (analyzer, outline, script, audio, postprocess)
- Populate `tools_registry` with all functions from `backend/tools/`
- Validate registry via admin API

**Affected Files:**
- `backend/scripts/seed_workflow_registry.py` (new)
- `backend/api/routes/admin.py` (add registry endpoints)

**Estimated Effort:** 1 day

### Step 3: Create Workflow Definition for `audiobook_generation`

**Actions:**
- Create `workflow_definitions` record: name='audiobook_generation'
- Create `workflow_revision` v1 with `is_published=TRUE`
- Create `workflow_steps` for v1: analysis, outline, approval, scripting, audio, post_processing
- Map each step to `agent_id` from `agents_registry`
- Set execution_mode: sequential for analysis/outline, concurrent for scripting/audio
- Validate structure (no circular deps, all agents exist)

**Affected Files:**
- `backend/scripts/create_audiobook_workflow_v1.py` (new seed script)
- `backend/api/routes/admin_workflows.py` (add workflow CRUD endpoints)

**Estimated Effort:** 1 day

### Step 4: Build Dynamic Workflow Loader

**Actions:**
- Create `backend/workflows/dynamic_loader.py`
- Implement `load_workflow_by_name(name, version=None) -> WorkflowRevision`
- Implement `build_workflow_from_revision(revision) -> WorkflowBuilder`
- Load agents via `importlib.import_module` + `getattr` on `factory_function`
- Validate input/output mappings at runtime
- Add caching for loaded workflows (LRU cache keyed by `revision_id`)

**Affected Files:**
- `backend/workflows/dynamic_loader.py` (new)
- `backend/workflows/runner.py` (new, runtime executor)

**Estimated Effort:** 2 days

### Step 5: Refactor AudiobookWorkflow to Use Dynamic Loader

**Actions:**
- Update `backend/workflows/audiobook_workflow.py` to accept `revision_id` in `__init__`
- Replace hardcoded SequentialBuilder/ConcurrentBuilder with `dynamic_loader.build_workflow_from_revision()`
- Keep existing `execute()` and `continue_after_approval()` methods but delegate to dynamic workflow
- Add fallback: if `revision_id` is None, use default hardcoded workflow (safety)

**Affected Files:**
- `backend/workflows/audiobook_workflow.py` (refactor `__init__`, `execute`, `continue_after_approval`)

**Estimated Effort:** 1 day

### Step 6: Update Task Runners to Create Workflow Instances

**Actions:**
- Modify `backend/tasks/audiobook_tasks.py::start_audiobook_workflow`
- On workflow start, create `workflow_instances` record with `job_id`, `revision_id` (current published revision)
- Update `workflow_instances.current_step_id` as workflow progresses
- Update `workflow_instances.instance_state` JSONB after each step
- On completion/failure, update `workflow_instances.status` and `completed_at`

**Affected Files:**
- `backend/tasks/audiobook_tasks.py` (update `_start_audiobook_workflow`, `_resume_audiobook_workflow`)
- `backend/workflows/audiobook_workflow.py` (add instance tracking)

**Estimated Effort:** 1 day

### Step 7: Add Admin UI for Workflow Editing

**Actions:**
- Create admin endpoints: `POST /api/v1/admin/workflows` (create new revision), `PUT /api/v1/admin/workflows/{id}/publish`
- Add validation: prevent editing published revisions (immutability)
- Add workflow version rollback: set `current_revision_id` to older version
- Frontend: add workflow editor page (optional for MVP, can be JSON-based initially)

**Affected Files:**
- `backend/api/routes/admin_workflows.py` (add workflow management endpoints)
- `src/pages/admin/WorkflowEditor.tsx` (new, optional)

**Estimated Effort:** 2 days

### Step 8: Add Monitoring and Rollback Safety

**Actions:**
- Add workflow execution telemetry (emit events to OpenTelemetry on step start/complete)
- Create admin endpoint `GET /api/v1/admin/workflows/instances?status=failed` (monitor failures)
- Implement canary rollout: allow % of jobs to use new revision (feature flag in `workflow_instances`)
- Add circuit breaker: if >10% of jobs fail on new revision, auto-rollback to previous
- Add workflow validation endpoint: `POST /api/v1/admin/workflows/{id}/validate` (dry-run without execution)

**Affected Files:**
- `backend/workflows/runner.py` (add telemetry, circuit breaker)
- `backend/api/routes/admin_workflows.py` (add monitoring endpoints)

**Estimated Effort:** 2 days

**Total Estimated Effort:** ~9–10 engineer-days (can be parallelized)

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Runtime failures due to invalid workflow definitions** (missing agents, circular dependencies) | HIGH | Comprehensive validation on `workflow_revisions` before allowing publish. Add dry-run test execution endpoint. Use DB constraints (FK integrity). Schema validation with Pydantic. |
| **Breaking changes to running jobs when switching workflow versions** | HIGH | Immutability: Published revisions cannot be edited. Each `workflow_instances` record locks to specific `revision_id`. Old jobs continue on old revisions. |
| **Performance degradation from dynamic loading and registry lookups** | MEDIUM | Cache loaded workflows in memory (LRU cache keyed by `revision_id`). Pre-load agents on startup. Use DB indexes on `workflow_id`, `revision_id`, `step_order`. |
| **Data migration complexity** (existing jobs have no `revision_id`) | MEDIUM | Add default `revision_id` (v1 hardcoded workflow) to `workflow_definitions`. Backfill existing `workflow_instances` with v1. New jobs auto-use `current_revision_id`. |
| **Loss of type safety when building workflows dynamically** | MEDIUM | Use Pydantic for `config_schema` validation in `agents_registry`. Add JSON schema validation on `input_mapping`/`output_mapping`. Runtime type checks in `dynamic_loader`. |
| **Increased complexity for developers debugging workflow issues** | LOW | Extensive logging in `dynamic_loader` and runner. Admin UI showing workflow DAG visualization. Include `revision_id` in all error messages and checkpoints. |

---

## Required Code Changes

### Files to Create

| Path | Purpose | Estimated LOC |
|------|---------|---------------|
| `backend/models/workflow_definition.py` | SQLAlchemy model for `workflow_definitions` table | ~60 |
| `backend/models/workflow_revision.py` | SQLAlchemy model for `workflow_revisions` table | ~80 |
| `backend/models/workflow_step.py` | SQLAlchemy model for `workflow_steps` table | ~120 |
| `backend/models/agent_registry.py` | SQLAlchemy model for `agents_registry` table | ~70 |
| `backend/models/tool_registry.py` | SQLAlchemy model for `tools_registry` table | ~60 |
| `backend/models/workflow_instance.py` | SQLAlchemy model for `workflow_instances` table (runtime tracking) | ~80 |
| `backend/db/migrations/versions/YYYYMMDD_add_workflow_schema.py` | Alembic migration to create 6 new tables | ~250 |
| `backend/workflows/dynamic_loader.py` | Core logic to load workflow from DB and construct agent_framework workflows | ~400 |
| `backend/workflows/runner.py` | Workflow execution runtime with telemetry and error handling | ~300 |
| `backend/scripts/seed_workflow_registry.py` | Seed `agents_registry` and `tools_registry` with existing code | ~200 |
| `backend/scripts/create_audiobook_workflow_v1.py` | Create default `audiobook_generation` workflow in DB | ~150 |
| `backend/api/routes/admin_workflows.py` | Admin CRUD endpoints for workflow definitions, revisions, validation | ~500 |
| `backend/api/schemas/workflow.py` | Pydantic schemas for workflow API requests/responses | ~200 |

### Files to Modify

| Path | Changes | Estimated LOC Changed |
|------|---------|----------------------|
| `backend/workflows/audiobook_workflow.py` | Refactor to use `dynamic_loader` while keeping fallback to hardcoded workflow | ~100 |
| `backend/tasks/audiobook_tasks.py` | Create `workflow_instances` records, update instance state during execution | ~80 |
| `backend/api/routes/admin.py` | Add registry list endpoints (agents, tools) | ~60 |
| `backend/main.py` | Register new `admin_workflows` router | ~5 |
| `backend/utils/checkpointing.py` | Optional: extend to link checkpoints to `workflow_instance_id` | ~20 |

**Total New Code:** ~2,500 LOC  
**Total Modified Code:** ~265 LOC

---

## Microsoft Agent Framework Integration

### Key Framework Features Used

| Feature | Usage in This Project | Documentation |
|---------|----------------------|---------------|
| **WorkflowBuilder.set_start_executor()** | Sets the initial executor for a workflow. Used in audiobook workflow for audio and post-processing stages. | [Create a Simple Sequential Workflow](https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/simple-sequential-workflow) |
| **WorkflowBuilder.with_checkpointing()** | Enables checkpointing with custom CheckpointStorage. Used with `PostgresCheckpointStorage` in audiobook_workflow.py. | [Checkpointing and Resuming Workflows](https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/checkpointing-and-resuming) |
| **workflow.run_stream() / run_stream_from_checkpoint()** | Async generator that streams workflow events. Used throughout audiobook workflow to process agent outputs incrementally. | [Workflows Core Concepts](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/core-concepts/workflows) |
| **AgentExecutor decorator pattern** | Wraps ChatAgent to make it executable in workflows. Used in all agent factories. | [Agents in Workflows](https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/agents-in-workflows) |
| **SequentialBuilder and ConcurrentBuilder** | Build workflows with sequential or concurrent agent execution. Used for analysis+outline (sequential) and script/audio generation (concurrent). | [Concurrent Orchestrations](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/core-concepts/edges) |
| **CheckpointStorage interface** | Abstract interface for checkpoint persistence. Implemented by `PostgresCheckpointStorage` in backend/utils/checkpointing.py. | [Checkpoints](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/checkpoints) |

### Authoritative Documentation References

- [Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)
- [Workflows Concepts](https://learn.microsoft.com/en-us/agent-framework/concepts/workflows)
- [Checkpointing and Resuming](https://learn.microsoft.com/en-us/agent-framework/concepts/checkpointing)
- [Create a Workflow](https://learn.microsoft.com/en-us/agent-framework/how-to/create-workflow)
- [Python API Reference](https://learn.microsoft.com/en-us/agent-framework/reference/python/agent-framework)

---

## Next Steps

### Immediate Actions (Priority Order)

1. **Create Alembic Migration for Workflow Schema** ✓ Ready to implement
   - Generate migration file: `alembic revision -m "add_workflow_schema"`
   - Define 6 tables with proper constraints and indexes
   - Test migration: `alembic upgrade head` and `alembic downgrade -1`

2. **Implement SQLAlchemy Models** ✓ Ready to implement
   - Create 6 model files in `backend/models/`
   - Add relationships and validators
   - Update `backend/models/__init__.py` to export new models

3. **Create Registry Seed Script** ✓ Ready to implement
   - Populate `agents_registry` with 5 existing agents
   - Populate `tools_registry` with all tools from `backend/tools/`
   - Add validation to ensure all agents/tools are importable

4. **Build Workflow Manager Service**
   - Implement loader, validator, and in-memory registry
   - Add caching for loaded workflows
   - Create unit tests

5. **Add Admin API Endpoints**
   - CRUD for workflow definitions and revisions
   - Validation and publish endpoints
   - Registry list endpoints

6. **Refactor Runtime Execution**
   - Update `AudiobookWorkflow` to use dynamic loader
   - Add fallback to hardcoded workflow
   - Create `workflow_instances` tracking

7. **Add Monitoring and Canary Rollouts**
   - Telemetry integration
   - Circuit breaker logic
   - Admin dashboards

### Questions to Resolve

1. **Notification Mechanism:** Prefer Postgres LISTEN/NOTIFY (Option A) or Redis pub/sub (Option B)?
   - **Recommendation:** Option A for simplicity (transactional), fallback to Option B for multi-host scale

2. **Workflow Instance ID:** Reuse `job.id` or create separate UUID?
   - **Recommendation:** Reuse `job.id` to reduce joins and maintain 1:1 relationship

3. **Admin UI:** Build JSON-based editor now or defer to post-MVP?
   - **Recommendation:** Start with JSON API, add visual editor after API is stable

### Ready to Implement

I'm ready to create the first implementation files. Would you like me to proceed with:
- ✅ Alembic migration for the 6-table workflow schema
- ✅ SQLAlchemy models for all 6 tables
- ✅ Registry seed script

Just confirm which step to start with, and I'll implement it with full tests and documentation.
