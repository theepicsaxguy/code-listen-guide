# Workflow DB Migration Plan

**Plan ID:** workflow-db-dynamic  
**Last Updated:** October 31, 2025  
**Status:** Implemented in backend (November 2025)

## Executive Summary

The hardcoded audiobook workflow now reads its orchestration from PostgreSQL. Published revisions are cached by the backend and each job is pinned to the revision it launched with. Checkpointing, job status updates, and admin tooling run on top of the same primitives, so new revisions can be authored, validated, and published without redeploying the API.

### Current State

- `backend/workflows/audiobook_workflow.py` now loads workflow revisions from Postgres, records step outputs in `workflow_instances`, and keeps checkpoints aligned with each step.
- `backend/workflows/dynamic_loader.py` provides `WorkflowManager`, which caches revisions, creates workflow instance rows, and keeps state snapshots current.
- `backend/tasks/audiobook_tasks.py` continues to bridge FastAPI background tasks to async execution while ensuring an instance row exists before each run.
- Agents remain defined in `backend/agents/` and are registered through the `agents_registry` seeding script, so new revisions reuse existing factories.
- Checkpoints still flow through `backend/utils/checkpointing.py::PostgresCheckpointStorage`, and Redis WebSocket updates work as before.

### Target State

- Workflows are versioned JSON revisions stored in Postgres and loaded on demand.
- `WorkflowManager` in `backend/workflows/dynamic_loader.py` caches published revisions and updates workflow instances as jobs progress.
- The admin API exposes workflow CRUD, revision creation, validation, and publish endpoints under `/api/v1/admin/workflows`.
- Running jobs stay pinned to their starting revision; instance state and checkpoints make restarts deterministic.
- Telemetry and circuit-breaker hooks can build on the persisted instance metadata (implementation TBD).

## Database Schema

We introduce six new tables. Revisions are immutable once published. All lookups index workflow and revision identifiers for fast fetches.

| Table | Purpose |
|-------|---------|
| `workflow_definitions` | Defines workflows and points to the currently published revision. |
| `workflow_revisions` | Holds immutable versions with metadata and publish markers. |
| `workflow_steps` | Stores ordered step definitions with agent bindings and execution hints. |
| `agents_registry` | Lists importable agent factories with config schemas and tool metadata. |
| `tools_registry` | Tracks reusable tools exposed to agents. |
| `workflow_instances` | Captures runtime state for each job and links to checkpoints. |

## Runtime Architecture

### Workflow Manager

`backend/workflows/dynamic_loader.py` ships the `WorkflowManager` singleton. It loads revisions with eager SQLAlchemy relationships, builds immutable descriptors (definition, steps, agent metadata), caches them in memory, and manages `workflow_instances` rows. Each update saves the serialized instance state so crashes can resume from the last completed step without re-running previous stages.

### Notification Watcher

Automatic hot reload via LISTEN/NOTIFY is still on the backlog. For now operators can call the publish endpoint (which refreshes the cache in-process) or manually restart workers if a stale revision needs clearing.

### Runner Flow

`backend/workflows/audiobook_workflow.py` binds each job to the published revision, streams agent responses step-by-step, persists outputs into the instance state, and reuses the existing checkpoint storage for audio and post-processing. `backend/tasks/audiobook_tasks.py` now ensures the instance row exists before execution and simply delegates to `execute()` or `continue_after_approval()`.

## Admin API Surface

`backend/api/routes/admin_workflows.py` exposes the new admin surface:

- `GET /api/v1/admin/workflows`
- `POST /api/v1/admin/workflows`
- `GET /api/v1/admin/workflows/{id}/revisions`
- `POST /api/v1/admin/workflows/{id}/revisions`
- `GET /api/v1/admin/workflows/{id}/revisions/{revision_id}`
- `POST /api/v1/admin/workflows/{id}/revisions/{revision_id}/validate`
- `POST /api/v1/admin/workflows/{id}/revisions/{revision_id}/publish`

Publishing runs inside a transaction, updates the definition pointer, and refreshes the in-process cache. Validation currently checks ordering, execution modes, and agent bindings; more advanced dry-runs can build on top of this scaffold.

## Safety Nets and Rollout

- **Immutability:** Published revisions are immutable; new drafts create new version numbers.
- **Canary:** Not yet implemented. Current rollout is all-or-nothing per publish, but the instance records keep enough metadata to support canaries later.
- **Circuit breaker:** Not yet implemented. Failure metrics can be calculated from `workflow_instances` and job status history.
- **Checkpoints:** Existing checkpoints remain valid and now pair with the stored instance state, so resuming a job reconstructs prior step outputs.
- **Telemetry:** The workflow still emits OpenTelemetry spans where previously instrumented; per-revision cost tracking remains a follow-up task.

## Implementation Snapshot

- Alembic migration `20251031_add_workflow_schema.py` and the SQLAlchemy models are active.
- Seed scripts populate `agents_registry`, `tools_registry`, and create the initial `audiobook_generation` revision.
- `WorkflowManager` handles revision caching and workflow instance lifecycle.
- `AudiobookWorkflow` executes stages dynamically (analysis → outline → approval → scripting → audio → post-processing) and persists outputs between restarts.
- Admin endpoints allow drafting, validating, and publishing revisions from the UI or API clients.

### Follow-up Work

1. LISTEN/NOTIFY or Redis pub/sub for cross-process hot reloads.
2. Canary rollout and circuit-breaker logic keyed off `workflow_instances` metrics.
3. Extended validation and dry-run tooling (mock agent execution, schema checks).
4. UI to visualize revisions and edit step graphs.
## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Invalid revisions hitting production | High | Enforce schema validation, dry-run builds, and import checks before publish. |
| Jobs flipping revisions mid-run | High | Pin `workflow_instances` to the revision ID captured at start. |
| Dynamic loading overhead | Medium | Cache builders per revision and preload agent factories. |
| Backfilling existing jobs | Medium | Seed baseline revision and backfill `workflow_instances` with that ID. |
| Debuggability | Medium | Log revision IDs everywhere, expose dashboards, keep admin audit trails. |

## Outstanding Decisions

1. **Notification transport** – Default to Postgres LISTEN/NOTIFY, keep Redis pub/sub as backup for multi-host deployments.
2. **Instance identity** – Reuse `jobs.id` for workflow instances to keep joins simple.
3. **Admin UI** – Launch with JSON editors; plan a richer visual builder once APIs stabilize.

## Reference Docs

- Microsoft Agent Framework documentation on workflows, checkpointing, and builders.  
- Existing project guides: `MIGRATION.md`, `DESIGN_SYSTEM.md`, and related decisions for style cues.

