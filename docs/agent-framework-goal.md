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
  - `model_identifier` and `provider` capture the upstream LLM pairing selected for the runtime factory.
  - `system_prompt` holds the bootstrap instructions surfaced to the agent factory and runtime.
  - `memory_pointers` records stable anchors (job-, repo-, or team-scoped) that the runtime forwards for downstream memory lookups.
  - `rollout_enabled`/`rollout_stage` expose launch gating so workflows can filter preview agents.
  - `access_policies` is a structured document with `default` and `overrides` sections; every rule lists allow/deny tool ids plus metadata for audit annotations.
  - `quota_limits` mirrors the policy structure with normalized limits (`limit`, `window`, `cooldown_seconds`) and optional override entries per subject.
- **Plugin schema:** Tables track plugin identity, version, owning team, authorization scopes, cost profile, and operational status. Workflows reference these ids to bind business logic to implementations.
- **Workflow schema:** Workflows are stored as ordered steps or graph edges that point to agent ids, expected outputs, guard conditions, and escalation paths. The workflow id is the key for tracing every execution.

### Plugin Registry
- **Code registry contract:** Each plugin module registers a stable slug, execute handler, and JSON schemas for inputs and outputs. Registry load fails if schema signatures drift from the database definition.
- **Surface to the LLM:** At session start the runtime passes the permitted plugin descriptors—name, summary, argument schema—to the LLM as function tools so it can plan within authorized capabilities only.

### Runtime Decision Cycle
1. Load the workflow step from the database, including the approved agent id and plugin allow-list.
2. Assemble context: agent system prompt, conversation memory pointers, step payload, plus the permitted tool descriptors.
3. Stream the LLM’s tool requests, logging each call/response pair in workflow state before executing anything.
4. Execute the plugin through the registry, return results to the LLM, persist the trace entry, and advance or branch the workflow.
5. Repeat the loop until the agent emits a final answer that requires no further tool calls, then surface that payload to downstream steps.

## Governance and Observability
- **Trace logging:** Persist workflow id, agent id, plugin slug, request payload, response payload, timestamps, cost metrics, and (when available) the LLM’s rationale. Make traces queryable for audits and RCA.
- **Policy enforcement:** Deny unauthorized or out-of-quota calls with structured errors that flow back to the LLM session. Record policy violations for analytics.
- **Integration hooks:** Stream trace events to observability, billing, and security systems without bypassing runtime validation.
- **Tool metrics:** Every tool invocation now emits OpenTelemetry counters and histograms for call counts, duration, and failure types, so operators can spot regressions quickly.
- **Billing handoff:** The workflow estimates per-call spend from registry metadata, sends each record to the billing service, and keeps a running summary in workflow state for later reconciliation.
- **Audit forwarding:** Authorization decisions, execution metrics, and cost payloads are bundled into the audit stream and delivered to the observability pipeline alongside the job timeline.

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
