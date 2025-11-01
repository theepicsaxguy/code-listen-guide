# Admin Operations Guide

## Workflow step overrides

- Open **Admin → Workflows → [Workflow]** to review the current revision.
- Each step now lists the tools it can call and the JSON `step_config` overrides applied to that step.
- Select **Configure** on a step to edit tool access. Use the checklist to allow registry tools or add a custom tool name when the registry has not been synchronized yet.
- Provide a JSON object to adjust `step_config` overrides. Leaving the field empty resets the step to inherit the agent defaults.
- Saving refreshes the workflow details panel so the updated policy and config are visible immediately.

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
