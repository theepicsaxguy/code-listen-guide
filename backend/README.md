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
- Workflow orchestration with Microsoft Agent Framework
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
├── agents/               # Microsoft Agent Framework agent factories
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
- PostgreSQL 15+
- FFmpeg (for audio processing)
- Azure Active Directory application with `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` configured for Azure OpenAI

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

5. **Set up PostgreSQL database**:
   ```bash
   createdb audiobook
   ```

6. **Run database migrations** (TODO: Set up Alembic):
   ```bash
   alembic upgrade head
   ```

### Running the Application

**Development mode:**

1. **Start FastAPI server**:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Kick off a workflow**:
   Create a job, then call `POST /api/v1/jobs/{job_id}/start`. The backend schedules the Microsoft Agent Framework workflow in a FastAPI background task, streams progress over WebSockets, and persists checkpoints in PostgreSQL.

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

### Payments
- `POST /api/v1/payments/create-intent` - Create payment intent
- `POST /api/v1/payments/webhook` - Stripe webhook handler
- `GET /api/v1/payments/history` - Payment history

### Player
- `GET /api/v1/player/{job_id}` - Get audiobook player data
- `GET /api/v1/player/{job_id}/download/{type}` - Download deliverable

## Workflow Lifecycle

Audiobook generation jobs move through several coordinated stages once a user starts a workflow:

1. **Analysis** – the Repository Analyzer agent clones the target repository, enumerates its files, and constructs a lightweight code map. Job status is set to `running` with stage `analysis`.
2. **Outline** – the Outline Generator agent converts the analysis into a chapter outline. The outline JSON is stored and the job transitions to `waiting_approval` while the system notifies connected clients over WebSocket.
3. **Scripting** – after approval, dedicated Script Writer agents work concurrently (one per chapter) and persist scripts as they complete. Progress events report chapter counts.
4. **Audio** – the Audio Producer agent batch-synthesizes narration files and uploads them to storage, storing URLs for each chapter.
5. **Post-processing** – the Post Processor agent stitches the audio, publishes deliverables, and marks the job `completed`.

Checkpoint records in PostgreSQL allow any stage to resume without repeating prior work. Clients can subscribe to the job channel to receive the JSON events emitted during each stage.

## Processing Pipeline

The audiobook generation uses a Microsoft Agent Framework workflow graph:

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
- **Azure OpenAI**: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT_NAME`, `AZURE_OPENAI_API_VERSION`
- **Other LLM/TTS Providers**: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`
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
- [ ] Implement Microsoft Agent Framework workflow logic
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
