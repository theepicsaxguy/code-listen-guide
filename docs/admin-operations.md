# Admin Operations Guide

## Workflow step overrides

- Open **Admin → Workflows → [Workflow]** to review the current revision.
- Each step now lists the tools it can call and the JSON `step_config` overrides applied to that step.
- Select **Configure** on a step to edit tool access. Use the checklist to allow registry tools or add a custom tool name when the registry has not been synchronized yet.
- Provide a JSON object to adjust `step_config` overrides. Leaving the field empty resets the step to inherit the agent defaults.
- Saving refreshes the workflow details panel so the updated policy and config are visible immediately.

## Plugin registry metadata

- Use **Admin → Plugins → Create Plugin** or **Edit** to keep the registry in sync with the backend contract.
- Each plugin row now surfaces slug, semantic version, owning team, authorization scope, approval mode, and the stored cost profile. Empty values show as dashes so gaps are easy to spot.
- When editing, populate the slug with the identifier published by the Python module and match the semantic version to the deployed build.
- Enter the authorization scope and approval mode as plain strings (for example `internal` or `manual`) so policy checks can read them verbatim.
- Paste the cost profile as valid JSON. The form validates the document before sending it to the API and rejects malformed payloads.

## Agent tool ordering

- Agents keep the tool order defined in the form. Dragging is not required—use the arrow buttons next to each tool to move it up or down.
- Removing a tool updates the list immediately and the API receives the filtered order on save.
- The module path and factory function inputs trim whitespace before submission; blank entries are blocked with inline errors so partial updates do not slip through.

## Streaming tool call trace

- Navigate to **Admin → Job Tracing** and search for a job ID.
- When a workflow trace is available, a new **Workflow Tool Trace** card renders a card for each step with status, run duration, and the allowed tool set.
- Every step now captures the user prompt, system instructions, and the model’s live reasoning stream before it reaches for a tool, so you can see what the agent was thinking.
- Expand a tool call to inspect input and output payloads, completion timestamps, and any surfaced errors. Running jobs refresh automatically every four seconds until completion.
- Assistant updates and final responses appear as their own entries, making it clear why a specific tool call or output happened.
- Stage progress and retry tooling remains unchanged, so operations staff can correlate stage errors with individual tool misfires.

## Policy & quota dashboard

- Open **Admin → Policy & Quotas** to view metrics returned by the policy engine.
- The top summary shows total policies, the last-day block count, and active overrides so you can gauge policy pressure at a glance.
- The **Quota Utilization** list highlights burn per policy with percentage badges and reset timers; progress bars go red when usage crosses 90%.
- The **Recent Blocked Calls** table surfaces the last ten blocks with policy names and reasons so the governance team can respond quickly.
- **Agent Access Controls** mirrors the current ACL state, separating allowed and blocked tool lists with the timestamp of the last change for audit trails.

## Refresh behavior

- Workflow step edits call the admin API immediately and the details page refetches once the request succeeds.
- Job tracing data refetches every four seconds while a job is running or queued; it stops polling after a terminal status is reached.
- Policy metrics rely on cached backend aggregations. Refresh the page to force a new fetch when you expect changes from enforcement rules.
