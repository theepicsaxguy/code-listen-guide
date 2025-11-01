# Goal Definition: Microsoft Agent Framework Orchestration

## Executive Summary
We need a runtime that lets an LLM steer work while the database keeps it inside the guardrails. The goal is a production Agent Framework deployment where the model can only call agents and plugins that our records explicitly allow, every request is validated before execution, and every action is logged for review.

## Context
- **Platform:** Microsoft Agent Framework for Python provides the runtime, tool calling surface, and workflow engine.
- **Source of truth:** A relational database already stores agents, plugins, workflows, and authorization policies. We treat it as the control plane.
- **Audience:** Platform engineers and governance teams who will extend the system, onboard new plugins, and review traces.

## Success Criteria
- Any LLM-issued call is blocked unless the database lists the agent, plugin, and permission in scope for the current workflow step.
- Plugin metadata exposed to the LLM (names, schemas, docs) always matches the registry implementation.
- Workflow traces can be replayed end-to-end, tying each model decision to inputs, outputs, and policy checks.
- Governance hooks (logging, quotas, policy violations) remain active even as plugins and agents change.

## Architecture Overview

### Database Control Plane
- **Agent schema:** Each record stores model/provider selection, system prompt, memory anchors, rollout flags, metadata, and the allow-listed plugin ids plus quotas. Agents never hard-code plugin names.
  - Access control lives in the `account_acl` JSON array, which enumerates the accounts allowed to instantiate the agent. An empty list keeps the agent open to all tenants.
  - Quota governance is captured by `quota_limits`, a JSON array of scope/limit objects (for example `{ "scope": "daily", "limit": 100 }`). An empty array means the platform applies no additional throttles.
  - Tool bindings rely on the `tools` JSON array, which now defaults to `[]` so every agent has an explicit allow list even when no plugins are required.
- **Plugin schema:** Tables track plugin identity, version, owning team, authorization scopes, cost profile, and operational status. Workflows reference these ids to bind business logic to implementations.
- **Workflow schema:** Workflows are stored as ordered steps or graph edges that point to agent ids, expected outputs, guard conditions, and escalation paths. The workflow id is the key for tracing every execution.

### Plugin Registry
- **Code registry contract:** Each plugin module registers a stable slug, execute handler, and JSON schemas for inputs and outputs. Registry load fails if schema signatures drift from the database definition.
- **Surface to the LLM:** At session start the runtime passes the permitted plugin descriptors—name, summary, argument schema—to the LLM as function tools so it can plan within authorized capabilities only.

### Runtime Decision Cycle
1. Load the workflow step from the database, including the approved agent id and plugin allow-list.
2. Assemble context: agent system prompt, conversation memory pointers, step payload, plus the permitted tool descriptors.
3. Capture the LLM’s requested plugin call and run a two-layer validation (database policy + registry schema).
4. Execute the plugin through the registry, return results to the LLM, persist the trace entry, and advance or branch the workflow.

## Governance and Observability
- **Trace logging:** Persist workflow id, agent id, plugin slug, request payload, response payload, timestamps, cost metrics, and (when available) the LLM’s rationale. Make traces queryable for audits and RCA.
- **Policy enforcement:** Deny unauthorized or out-of-quota calls with structured errors that flow back to the LLM session. Record policy violations for analytics.
- **Integration hooks:** Stream trace events to observability, billing, and security systems without bypassing runtime validation.

## Operating Assumptions
- Agent Framework’s Python runtime handles tool execution and workflow orchestration.
- The database already exposes CRUD operations for agents, plugins, workflows, and policy metadata.
- Plugins are Python modules registered at startup and must publish machine-readable schemas.
- The deployed LLM supports tool/function calling compliant with Agent Framework expectations.

## Open Questions
- How do we version plugin schemas in the database so historical traces stay readable after upgrades?
- What retry/backoff strategy should the runtime apply when plugin executions fail due to transient errors?
- Do we need a human override workflow for policy violations, or is automatic failure sufficient for launch?

## Next Steps
- Finalize database migrations that capture the agent, plugin, workflow, and policy fields referenced here.
- Implement automated conformance checks that compare registry schemas with database definitions on deploy.
- Define retention and access policies for workflow traces to satisfy compliance requirements.
