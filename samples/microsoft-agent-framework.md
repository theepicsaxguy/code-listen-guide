# Microsoft Agent Framework Samples

These notes capture the pieces of Microsoft's Agent Framework documentation that still apply to Codebase Audiobook without leaning on any single-cloud exclusives. The goal is to show how the SDK powers our multi-agent workflow while keeping the provider mix focused on OpenAI and Anthropic.

## What Matters for This Project
- Install `agent-framework` from the prerelease channel to access the workflow and agent abstractions we use in production.
- Wire the `OpenAIResponsesClient` into each agent. The framework speaks the same API surface for Anthropic so we can swap providers without touching orchestration code.
- Keep observability enabled through OpenTelemetry. The framework exposes hooks for spans and metrics that align with our FastAPI deployment.

## Cleaned Up Content
We removed the previous vendor-specific export (`microsoft-agent-framework-7cbbaca7f4a0dab1.txt`) because it only covered CLI authentication flows and deployment steps we no longer support. Anything we keep in this folder should apply regardless of which LLM vendor we use.

If you need detailed walkthroughs for the SDK, go straight to the official docs and focus on the orchestration primitives (`WorkflowBuilder`, `ChatAgent`, `AgentExecutor`).
