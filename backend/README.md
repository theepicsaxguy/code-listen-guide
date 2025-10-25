# Codebase Audiobook - Backend

This is the backend API for the Codebase Audiobook service, built with FastAPI and Python.

## Overview

The backend handles:
- User authentication and authorization
- Repository analysis and code parsing
- AI-powered chapter outline generation
- Narration script generation using Claude
- Text-to-speech audio synthesis
- Payment processing with Stripe
- Workflow orchestration with Agent Framework
- File storage with AWS S3

## Project Structure

```
backend/
├── api/                    # API routes and schemas
│   ├── events.py         # WebSocket event bridge
│   ├── routes/           # HTTP endpoint handlers
│   │   ├── auth.py
│   │   ├── jobs.py
│   │   ├── outlines.py
│   │   ├── payments.py
│   │   └── player.py
│   ├── schemas/          # Pydantic request/response models
│   │   ├── chapter.py
│   │   ├── job.py
│   │   ├── outline.py
│   │   ├── payment.py
│   │   └── user.py
│   └── ws.py             # Broadcast helper
├── agents/               # Agent Framework agent factories
│   ├── __init__.py
│   ├── analyzer_agent.py
│   ├── audio_agent.py
│   ├── outline_agent.py
│   ├── postprocess_agent.py
│   └── script_agent.py
├── db/
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── versions/
│   │       └── 20241025_add_workflow_checkpoints.py
│   └── session.py
├── models/
│   ├── chapter.py
│   ├── deliverable.py
│   ├── job.py
│   ├── outline.py
│   ├── payment.py
│   ├── usage_log.py
│   ├── user.py
│   └── workflow_checkpoint.py
├── tasks/
│   └── audiobook_tasks.py
├── tools/                 # Helper functions exposed as agent tools
│   ├── __init__.py
│   ├── audio_tools.py
│   ├── code_parser_tools.py
│   ├── db_tools.py
│   ├── git_tools.py
│   └── storage_tools.py
├── utils/
│   ├── auth.py
│   ├── checkpointing.py
│   └── validators.py
├── workflows/
│   └── audiobook_workflow.py
├── config.py
├── main.py
├── requirements.txt
└── .env.example
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (required for production; local development defaults to SQLite)
- FFmpeg (for audio processing)
- libxml2-dev and libxslt1-dev (required to build the `lxml` dependency used by Docling)
- OpenAI account with an API key and optional custom base URL or model overrides

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repo-url>
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

5. **Set up the database**:
   - With PostgreSQL:
     ```bash
     createdb audiobook
     ```
   - With the default SQLite database no action is required; the API will create the `backend_dev.db` file on startup.

6. **Run database migrations**:
   ```bash
   alembic -c backend/alembic.ini upgrade head
   ```
   The configuration file points Alembic at the models under `backend/models` and
   reads connection details from your `.env`.

### Running the Application

**Development mode:**

1. **Start FastAPI server**:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Kick off a workflow**:
   Create a job, then call `POST /api/v1/jobs/{job_id}/start`. The backend schedules the Agent Framework workflow in a FastAPI background task, streams progress over WebSockets, and persists checkpoints in PostgreSQL.

**Access the API:**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh access token

## Security

- Cross-origin requests are limited to the configured frontend URLs with explicit method and header allowlists.
- Standard security headers (CSP, HSTS, Referrer-Policy, Permissions-Policy, X-Frame-Options, X-Content-Type-Options) are applied to every response.
- A shared rate limiter enforces per-client quotas using SlowAPI, with tighter limits on registration, login, and token refresh endpoints.

### Jobs
- `POST /api/v1/jobs` - Create new audiobook job
- `GET /api/v1/jobs` - List user's jobs
- `GET /api/v1/jobs/{job_id}` - Get job details
- `DELETE /api/v1/jobs/{job_id}` - Delete job
- `POST /api/v1/jobs/{job_id}/start` - Start or resume workflow execution

### Outlines
- `POST /api/v1/jobs/{job_id}/outline` - Generate chapter outline
- `PUT /api/v1/jobs/{job_id}/outline` - Update outline
- `POST /api/v1/jobs/{job_id}/outline/approve` - Approve and pay

Clients submit repository analysis JSON to the generation endpoint. The backend runs the outline agent, normalizes chapter
durations, persists the outline, and moves the job into the `waiting_approval` stage. Updates accept the full outline payload
plus optional `user_modifications`, reset approval flags, and overwrite the stored JSON. Approvals require an `outline_id` and
return a Stripe payment intent; if a successful payment already exists the workflow resumes immediately after the outline is
marked as approved.

### Payments
- `POST /api/v1/payments/create-intent` - Create payment intent
- `POST /api/v1/payments/webhook` - Stripe webhook handler
- `GET /api/v1/payments/history` - Payment history

### Player
- `GET /api/v1/player/{job_id}` - Get audiobook player data
- `GET /api/v1/player/{job_id}/download/{type}` - Download deliverable

### Real-time updates
- `WS /ws/jobs/{job_id}` - Subscribe to JSON progress events for a job

## Workflow Lifecycle

Audiobook generation jobs move through several coordinated stages once a user starts a workflow:

1. **Analysis** – the Repository Analyzer agent clones the target repository, enumerates its files, and constructs a lightweight code map. Job status is set to `running` with stage `analysis`.
2. **Outline** – the Outline Generator agent converts the analysis into a chapter outline. The outline JSON is stored and the job transitions to `waiting_approval` while the system notifies connected clients over WebSocket.
3. **Scripting** – after approval, dedicated Script Writer agents work concurrently (one per chapter) and persist scripts as they complete. Progress events report chapter counts.
4. **Audio** – the Audio Producer agent batch-synthesizes narration files and uploads them to storage, storing URLs for each chapter.
5. **Post-processing** – the Post Processor agent stitches the audio, publishes deliverables, and marks the job `completed`.

Download links exposed through the player API are signed at request time so clients
receive time-limited access to chapter audio and bundle archives stored in S3.

## Checkpoint storage

Workflow progress is persisted in the `workflow_checkpoints` table. The helpers in
`backend/utils/checkpointing.py` wrap the `PostgresCheckpointStorage` implementation
and accept an optional SQLAlchemy session. Workflows call `save_checkpoint` with a
workflow identifier, step name, and JSON-serializable state; `load_checkpoint` and
the related helpers return the stored payloads so runs can resume cleanly.

Checkpoint records in PostgreSQL allow any stage to resume without repeating prior work. Clients can subscribe to the job channel to receive the JSON events emitted during each stage.

## Processing Pipeline

Every AI-heavy stage now flows through the Agent Framework. Each service composes an OpenAI responses client,
creates the appropriate agent, and lets that agent orchestrate tool calls. Manual Anthropic or bespoke OpenAI integrations have been
removed so there is a single, auditable execution path for analysis, outlining, scripting, audio, and post-processing.

The audiobook generation uses an Agent Framework workflow graph:

1. **Repository Analysis** (`RepositoryAnalyzer` agent)
   - Clone the repository
   - Parse code with tree-sitter
   - Produce dependency and complexity summaries

2. **Outline Generation** (`OutlineGenerator` agent)
   - Draft chapter plan based on analysis depth tier
   - Capture estimated durations and learning objectives

3. **Human Approval** (`HumanApproval` handoff)
   - Present outline for user review
   - Pause the workflow until approval or change request

4. **Script Generation** (`ScriptWriter` agent team)
   - Generate narration scripts in parallel batches
   - Persist scripts and token usage per chapter

5. **Audio Synthesis** (`AudioProducer` agent team)
   - Convert scripts to audio while streaming progress
   - Upload chapter files to S3 and capture metadata

6. **Post-Processing** (`PostProcessor` agent)
   - Merge chapter audio, create metadata, and push final deliverables to storage
   - Emit completion events so the UI can update in real time

## Environment Variables

See `.env.example` for required environment variables:

- **Database**: `DATABASE_URL`, `CHECKPOINT_DATABASE_URL`
- **OpenAI**: `OPENAI_API_KEY`, `OPENAI_RESPONSES_MODEL`, `OPENAI_BASE_URL`
- **Anthropic**: `ANTHROPIC_API_KEY`
- **Stripe**: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`
- **AWS**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME`, `S3_REGION`
- **Auth**: `JWT_SECRET`, `CLERK_SECRET_KEY`
- **Observability**: `SENTRY_DSN`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`

## Development

### Running Tests

TODO: Set up pytest

```bash
pytest
```

### Code Formatting

```bash
black .
flake8 .
mypy .
```

### Database Migrations

TODO: Set up Alembic

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Deployment

See `BACKEND_IMPLEMENTATION_PLAN.md` for deployment instructions.

**Recommended platforms:**
- Railway
- Render
- AWS ECS

## TODO

This backend structure has been scaffolded with comprehensive TODO comments in each file. See individual files for implementation tasks.

Major remaining work:
- [ ] Implement all service methods
- [ ] Implement all API route handlers
- [ ] Set up Alembic database migrations
- [ ] Implement Agent Framework workflow logic
- [ ] Add comprehensive error handling
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Set up CI/CD pipeline
- [ ] Configure production deployment
- [ ] Add API rate limiting
- [ ] Add request validation
- [ ] Implement caching strategies
- [ ] Add comprehensive logging
- [ ] Set up monitoring and alerts

## Reference

See `BACKEND_IMPLEMENTATION_PLAN.md` for the complete implementation plan with architecture diagrams, cost analysis, and detailed specifications.
