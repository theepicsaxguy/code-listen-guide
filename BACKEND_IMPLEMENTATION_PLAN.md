# Microsoft Agent Framework Integration Plan for Codebase Audiobook

## Executive Summary

The Microsoft Agent Framework (released October 2024) is the unified successor to AutoGen and Semantic Kernel, providing enterprise-grade multi-agent orchestration with support for Python and .NET. This plan details how to integrate it into the Codebase Audiobook backend so we can replace the Celery-based concepts in the scaffold with an intelligent, agentic workflow system.

## Why Microsoft Agent Framework?

### Key Benefits for Codebase Audiobook

1. **Multi-agent orchestration**: Perfect for our multi-stage pipeline (analysis → outline → scripting → audio → post-processing)
2. **Built-in checkpointing**: Resume long-running audiobook generation jobs after failures
3. **Graph-based workflows**: Explicit control over execution paths with type safety
4. **Human-in-the-loop**: Easy to add approval steps (outline acceptance)
5. **OpenTelemetry integration**: Production-ready observability out of the box
6. **MCP support**: Can integrate with Model Context Protocol servers for code analysis
7. **Enterprise features**: Thread-based state management, filters, telemetry
8. **Streaming support**: Stream chapter generation progress to users in real time

### Advantages Over the Celery Scaffold

| Feature | Celery (Scaffolded Plan) | Microsoft Agent Framework |
|---------|--------------------------|----------------------------|
| Multi-agent coordination | Manual orchestration | Built-in patterns (sequential, concurrent, handoff) |
| State management | Custom Redis/DB logic | Thread-based state with checkpoints |
| Error recovery | Manual retry logic | Automatic checkpointing and resume |
| Observability | Custom Sentry integration | OpenTelemetry built in |
| Type safety | Minimal (Python dictionaries) | Strong typing with validation |
| LLM integration | Direct API calls | Native agent abstractions |
| Human approval | Custom workflow | Built-in human-in-the-loop patterns |
| Complexity | High (manual wiring) | Lower (declarative workflows) |

---

## Architecture Overview with Agent Framework

### System Components

```
┌─────────────┐
│   FastAPI   │ (REST API - Job submission, progress tracking)
│  Application│
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│    Microsoft Agent Framework Runtime         │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │     Audiobook Workflow Graph       │    │
│  │                                    │    │
│  │  [Analyzer] → [Outliner]          │    │
│  │       ↓            ↓               │    │
│  │  [Approval] → [ScriptTeam]        │    │
│  │                    ↓               │    │
│  │              [AudioTeam]           │    │
│  │                    ↓               │    │
│  │            [PostProcessor]         │    │
│  └────────────────────────────────────┘    │
│                                              │
│  Checkpoints stored in PostgreSQL           │
└──────────────────────────────────────────────┘
       │
       ├──→ OpenAI / Anthropic Claude
       ├──→ OpenAI TTS
       ├──→ PostgreSQL (state + data)
       └──→ S3 (audio files)
```

### Agent Definitions

We will create specialized agents for each stage:

1. **RepositoryAnalyzer agent**: Clones repo, parses code, builds dependency graph
2. **OutlineGenerator agent**: Creates chapter structure using Claude
3. **ScriptWriter agents**: Team of agents (1 per chapter) generating narration scripts
4. **AudioProducer agents**: Team of agents (1 per chapter) synthesizing audio
5. **PostProcessor agent**: Combines audio, creates deliverables
6. **HumanApproval agent**: Handles user outline approval with handoff pattern

---

## Implementation Architecture

### Project Structure

```
backend/
├── main.py                          # FastAPI application
├── config.py                        # Configuration
├── requirements.txt
│
├── agents/                          # Agent definitions
│   ├── __init__.py
│   ├── analyzer_agent.py           # Repository analysis agent
│   ├── outline_agent.py            # Outline generation agent
│   ├── script_agent.py             # Script generation agent
│   ├── audio_agent.py              # Audio synthesis agent
│   ├── postprocess_agent.py        # Post-processing agent
│   └── approval_agent.py           # Human approval handler
│
├── workflows/                       # Workflow definitions
│   ├── __init__.py
│   ├── audiobook_workflow.py       # Main workflow orchestration
│   └── workflow_types.py           # Workflow state types
│
├── tools/                          # Agent tools (functions agents can call)
│   ├── __init__.py
│   ├── git_tools.py               # Git clone, file operations
│   ├── code_parser_tools.py       # Tree-sitter code parsing
│   ├── storage_tools.py           # S3 upload/download
│   ├── audio_tools.py             # FFmpeg operations
│   └── db_tools.py                # Database operations
│
├── api/                            # FastAPI endpoints
│   ├── routes/
│   │   ├── jobs.py                # Job CRUD
│   │   ├── workflows.py           # Workflow trigger and status
│   │   └── webhooks.py            # Payment webhooks
│
├── models/                         # SQLAlchemy models
│   └── ...                         # Same as before
│
└── utils/
    └── checkpointing.py            # Checkpoint storage/retrieval
```

---

## Installation and Setup

### Dependencies

```
pip install agent-framework --pre
pip install anthropic openai boto3 stripe tree-sitter
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi
```

### Environment Variables

```
OPENAI_API_KEY=sk-openai-xxxxx
OPENAI_RESPONSES_MODEL=gpt-4o-mini

DATABASE_URL=postgresql://user:password@localhost:5432/audiobook
CHECKPOINT_DATABASE_URL=postgresql://user:password@localhost:5432/audiobook

AWS_ACCESS_KEY_ID=xxxxx
AWS_SECRET_ACCESS_KEY=xxxxx
S3_BUCKET_NAME=codebase-audiobooks

OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

---

## Agent Implementation Examples

### Repository Analyzer Agent

```python
from agent_framework import Agent
from agent_framework.tools import FunctionTool
from tools.git_tools import clone_repository
from tools.code_parser_tools import parse_codebase_structure

async def create_analyzer_agent(chat_client):
    tools = [
        FunctionTool(
            name="clone_repository",
            description="Clone a GitHub repository",
            func=clone_repository,
        ),
        FunctionTool(
            name="parse_codebase_structure",
            description="Parse codebase using tree-sitter",
            func=parse_codebase_structure,
        ),
    ]

    return Agent(
        name="RepositoryAnalyzer",
        instructions="""
        You are a senior software architect specializing in code analysis.
        Clone the repository, analyse the codebase, and return structured JSON.
        """,
        tools=tools,
        chat_client=chat_client,
    )
```

### Outline Generator Agent

```python
from agent_framework import Agent

async def create_outline_agent(chat_client):
    return Agent(
        name="OutlineGenerator",
        instructions="""
        You are an expert technical writer. Create a comprehensive audiobook outline
        with durations, objectives, and referenced files.
        """,
        chat_client=chat_client,
    )
```

### Script Writer Agent

```python
from agent_framework import Agent
from agent_framework.tools import FunctionTool
from tools.db_tools import save_chapter_script

async def create_script_agent(chat_client, chapter_context: dict):
    tools = [
        FunctionTool(
            name="save_script",
            description="Persist chapter script",
            func=save_chapter_script,
        )
    ]

    return Agent(
        name=f"ScriptWriter_Chapter{chapter_context['chapter_number']}",
        instructions="""
        Write an engaging narration script that explains every component listed in the
        chapter context without dumping raw code.
        """,
        tools=tools,
        chat_client=chat_client,
    )
```

### Audio Producer Agent

```python
from agent_framework import Agent
from agent_framework.tools import FunctionTool
from tools.audio_tools import synthesize_speech
from tools.storage_tools import upload_to_s3

async def create_audio_agent(chat_client):
    tools = [
        FunctionTool(
            name="synthesize_speech",
            description="Convert text to audio",
            func=synthesize_speech,
        ),
        FunctionTool(
            name="upload_audio_to_s3",
            description="Upload audio file to S3",
            func=upload_to_s3,
        ),
    ]

    return Agent(
        name="AudioProducer",
        instructions="""
        Convert scripts into high-quality MP3 audio, normalise levels, and upload to S3.
        """,
        tools=tools,
        chat_client=chat_client,
    )
```

---

## Workflow Orchestration

### Main Audiobook Workflow

```python
from agent_framework import WorkflowContext
from workflows.types import AudiobookState
from agents import (
    create_analyzer_agent,
    create_outline_agent,
    create_script_agent,
    create_audio_agent,
    create_postprocess_agent,
    create_approval_agent,
)

class AudiobookWorkflow:
    def __init__(self, chat_client, job_id: str, repo_url: str, depth_tier: str):
        self.chat_client = chat_client
        self.job_id = job_id
        self.repo_url = repo_url
        self.depth_tier = depth_tier
        self.context = WorkflowContext(checkpoint_store=PostgreSQLCheckpointStore(job_id))

    async def execute(self):
        analysis = await (await create_analyzer_agent(self.chat_client)).run(
            f"Analyze repository {self.repo_url}"
        )
        self.context.set("analysis", analysis)
        await self.context.checkpoint("analysis")

        outline = await (await create_outline_agent(self.chat_client)).run(
            f"Create a {self.depth_tier} outline from this analysis: {analysis}"
        )
        self.context.set("outline", outline)
        await self.context.checkpoint("outline")

        approved_outline = await (await create_approval_agent()).run_with_handoff(
            outline_data=outline,
            timeout_seconds=86400,
        )
        self.context.set("approved_outline", approved_outline)
        await self.context.checkpoint("approval")

        scripts = await self._generate_scripts(approved_outline)
        self.context.set("scripts", scripts)
        await self.context.checkpoint("scripts")

        audio_files = await self._synthesize_audio(scripts)
        self.context.set("audio_files", audio_files)
        await self.context.checkpoint("audio")

        deliverables = await (await create_postprocess_agent(self.chat_client)).run(
            {
                "job_id": self.job_id,
                "audio_files": audio_files,
            }
        )
        await self.context.checkpoint("deliverables")
        return deliverables

    async def _generate_scripts(self, outline):
        tasks = []
        for chapter in outline["chapters"]:
            agent = await create_script_agent(self.chat_client, chapter)
            tasks.append(agent.run(f"Write script for chapter {chapter['number']}"))
        return await asyncio.gather(*tasks)

    async def _synthesize_audio(self, scripts):
        agent = await create_audio_agent(self.chat_client)
        tasks = []
        for index, script in enumerate(scripts, start=1):
            tasks.append(
                agent.run(
                    f"Convert to audio and upload to S3 as jobs/{self.job_id}/chapters/{index}.mp3:\n{script}"
                )
            )
        return await asyncio.gather(*tasks)
```

### Declarative Workflow Graph

```yaml
name: AudiobookGeneration
executors:
  - id: analyzer
    type: agent
    agent: RepositoryAnalyzer
  - id: outliner
    type: agent
    agent: OutlineGenerator
  - id: approval
    type: human_approval
    timeout: 86400
  - id: script_team
    type: concurrent_agents
    agent_factory: ScriptWriterFactory
    parallelism: 10
  - id: audio_team
    type: concurrent_agents
    agent_factory: AudioProducerFactory
    parallelism: 5
  - id: postprocessor
    type: agent
    agent: PostProcessor

edges:
  - from: start
    to: analyzer
  - from: analyzer
    to: outliner
  - from: outliner
    to: approval
  - from: approval
    to: script_team
  - from: script_team
    to: audio_team
  - from: audio_team
    to: postprocessor
  - from: postprocessor
    to: end
```

---

## FastAPI Integration

### Workflow Trigger Endpoint

```python
from fastapi import APIRouter, BackgroundTasks, HTTPException
from agent_framework.openai import OpenAIResponsesClient
from backend.config import get_settings
from workflows.audiobook_workflow import AudiobookWorkflow

router = APIRouter()

@router.post("/jobs/{job_id}/start-workflow")
async def start_audiobook_workflow(job_id: str, background_tasks: BackgroundTasks):
    job = await fetch_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "pending":
        raise HTTPException(status_code=400, detail="Job already started")

    settings = get_settings()
    chat_client = OpenAIResponsesClient(
        api_key=settings.openai_api_key,
        model_id=settings.openai_responses_model,
    )
    workflow = AudiobookWorkflow(chat_client, job_id, job.repo_url, job.depth_tier)
    background_tasks.add_task(workflow.execute)
    await mark_job_running(job_id)
    return {"status": "workflow_started"}
```

### Workflow Status Endpoint

```python
@router.get("/jobs/{job_id}/workflow-status")
async def get_workflow_status(job_id: str):
    checkpoint = await load_checkpoint(job_id)
    if not checkpoint:
        return {"status": "not_started"}
    return {
        "status": checkpoint["state"].get("current_stage"),
        "progress": checkpoint["state"].get("progress_percentage"),
        "next_executor": checkpoint["state"].get("next_executor"),
    }
```

---

## Checkpointing Implementation

### PostgreSQL Checkpoint Storage

```python
from agent_framework.workflows import CheckpointStore
from backend.db.session import SessionLocal
from backend.models.workflow_checkpoint import WorkflowCheckpoint

class PostgreSQLCheckpointStore(CheckpointStore):
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.db = SessionLocal()

    async def save_checkpoint(self, executor_id: str, state: dict):
        checkpoint = WorkflowCheckpoint(
            job_id=self.job_id,
            executor_id=executor_id,
            state_data=state,
        )
        self.db.add(checkpoint)
        self.db.commit()

    async def load_latest_checkpoint(self) -> dict | None:
        checkpoint = (
            self.db.query(WorkflowCheckpoint)
            .filter(WorkflowCheckpoint.job_id == self.job_id)
            .order_by(WorkflowCheckpoint.created_at.desc())
            .first()
        )
        if not checkpoint:
            return None
        return {
            "executor_id": checkpoint.executor_id,
            "state": checkpoint.state_data,
            "timestamp": checkpoint.created_at,
        }
```

---

## Observability and Monitoring

### OpenTelemetry Integration

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))
FastAPIInstrumentor.instrument_app(app)
```

### Custom Metrics

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)
chapters_generated = meter.create_counter("audiobook.chapters.generated")
audio_synthesis_duration = meter.create_histogram("audiobook.audio.duration")
llm_tokens_used = meter.create_counter("audiobook.llm.tokens")
```

---

## Cost Optimisation

### Token Usage Tracking

```python
from agent_framework.middleware import TokenCountingMiddleware

def create_script_agent_with_budget(chat_client, chapter_context: dict, max_tokens: int = 4000):
    token_counter = TokenCountingMiddleware(max_tokens=max_tokens)
    return Agent(
        name=f"ScriptWriter_Chapter{chapter_context['chapter_number']}",
        instructions="...",
        chat_client=chat_client,
        middleware=[token_counter],
    )
```

### Concurrent Execution Limits

```python
MAX_CONCURRENT_SCRIPTS = 5

async def generate_scripts_in_batches(chapters, chat_client):
    scripts = []
    for i in range(0, len(chapters), MAX_CONCURRENT_SCRIPTS):
        batch = chapters[i : i + MAX_CONCURRENT_SCRIPTS]
        tasks = [create_script_agent(chat_client, chapter).run("...") for chapter in batch]
        scripts.extend(await asyncio.gather(*tasks))
        await asyncio.sleep(2)
    return scripts
```

---

## Error Handling and Recovery

```python
from agent_framework import WorkflowExecutionError

async def execute_with_retry(workflow, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            checkpoint = await workflow.context.load_checkpoint()
            if checkpoint:
                return await workflow.resume(checkpoint)
            return await workflow.execute()
        except WorkflowExecutionError as exc:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(60)
```

---

## Migration Path from the Celery Scaffold

### Phase 1: Hybrid

Keep Celery tasks for simple fire-and-forget jobs while the Agent Framework workflow runs the audiobook pipeline. The API calls the Agent Framework runner, while Celery handles small utilities such as email notifications.

### Phase 2: Full Agent Framework

Deprecate Celery tasks and move all orchestration to Agent Framework once confidence is high.

---

## Comparison: Before and After

### Before (Celery Scaffold)

```python
workflow = chain(
    analyze_repository.s(job_id),
    generate_outline.s(job_id),
    generate_all_scripts.s(job_id),
    synthesize_all_audio.s(job_id),
    post_process_deliverables.s(job_id),
)
workflow.apply_async()
```

### After (Agent Framework)

```python
workflow = AudiobookWorkflow(chat_client, job_id, repo_url, depth_tier)
result = await workflow.execute()
```

---

## Implementation Checklist

### Phase 1: Foundation
- [ ] Install agent-framework and dependencies
- [ ] Set up OpenAI or Anthropic API access
- [ ] Configure OpenTelemetry for observability
- [ ] Create checkpoint storage in PostgreSQL
- [ ] Define workflow state types

### Phase 2: Core Agents
- [ ] Implement RepositoryAnalyzer agent with git tools
- [ ] Implement OutlineGenerator agent
- [ ] Implement ScriptWriter agent template
- [ ] Implement AudioProducer agent with TTS tools
- [ ] Implement PostProcessor agent
- [ ] Implement HumanApproval agent

### Phase 3: Workflow Orchestration
- [ ] Build AudiobookWorkflow class
- [ ] Implement sequential stages (analysis → outline → approval)
- [ ] Add concurrent script generation
- [ ] Add concurrent audio synthesis
- [ ] Integrate checkpointing at each stage
- [ ] Add error handling and retry logic

### Phase 4: API Integration
- [ ] Create workflow trigger endpoint
- [ ] Build workflow status endpoint
- [ ] Add resume workflow endpoint
- [ ] Implement progress tracking with streaming updates
- [ ] Add webhook for outline approval

### Phase 5: Testing
- [ ] Test with small repositories
- [ ] Test checkpoint save/resume functionality
- [ ] Test concurrent execution limits
- [ ] Validate cost tracking accuracy
- [ ] Load test with multiple simultaneous workflows

### Phase 6: Monitoring
- [ ] Set up OpenTelemetry dashboard
- [ ] Create metrics for chapters, tokens, and costs
- [ ] Add alerting for workflow failures
- [ ] Implement cost tracking per job
- [ ] Add performance profiling

### Phase 7: Production Deployment
- [ ] Deploy FastAPI + Agent Framework runtime
- [ ] Configure production OpenTelemetry endpoint
- [ ] Set up checkpoint cleanup jobs
- [ ] Add workflow cancellation support
- [ ] Enable distributed tracing across services

---

## Key Advantages Summary

1. **State management**: Thread-based context with automatic checkpointing
2. **Orchestration**: Built-in sequential, concurrent, and handoff patterns
3. **Type safety**: Strong typing prevents runtime bugs
4. **Observability**: OpenTelemetry instrumentation is first-class
5. **Human in the loop**: Outline approvals fit naturally
6. **Error recovery**: Automatic resume from checkpoints
7. **LLM integration**: Native abstractions for chat models
8. **Scalability**: Distributed execution support

---

## Cost Impact

### Development Time

- Celery plan: 6–8 weeks
- Agent Framework plan: 4–5 weeks (≈30% faster)

Reasons:
- No custom orchestration plumbing
- Checkpointing and telemetry are ready-made
- Type safety reduces debugging time

### Operational Cost

- Automatic retry reduces manual intervention
- Checkpointing prevents rerunning expensive LLM calls
- Observability accelerates debugging
- Token tracking middleware prevents budget overruns

---

## Recommended Approach

Start with Microsoft Agent Framework immediately. Skip building the Celery workflow because the framework removes boilerplate, ships with production-ready observability, and matches the audiobook pipeline perfectly.

Implementation order:

1. Install Agent Framework and validate with a simple agent
2. Build RepositoryAnalyzer + OutlineGenerator agents
3. Create basic workflow (analysis → outline)
4. Test checkpointing and resume
5. Expand to the full workflow with script/audio teams
6. Deploy with telemetry enabled

---

## Open Questions

1. OpenAI vs. Anthropic for each agent stage?
2. API keys vs. cloud identity providers for local development?
3. Deploy Agent Framework runtime alongside FastAPI or as a separate worker?
4. Single TTS voice or multiple voices per chapter?
5. PostgreSQL vs. dedicated store for checkpoints?

Recommendation: use Anthropic Claude for scripts, OpenAI responses for analysis/outlining, deploy workflow with FastAPI on Railway, and persist checkpoints in PostgreSQL.

---

## Next Steps

1. Install Microsoft Agent Framework and run a smoke test
2. Scaffold repository analyzer and outline generator agents
3. Connect workflow trigger endpoint to the runner
4. Implement checkpoint persistence and resume flow
5. Expand to full pipeline with monitoring and cost controls
6. Ship the Agent Framework-based backend
