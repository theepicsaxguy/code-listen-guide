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
│   ├── routes/            # HTTP endpoint handlers
│   │   ├── auth.py       # Authentication routes
│   │   ├── jobs.py       # Job management routes
│   │   ├── outlines.py   # Outline generation routes
│   │   ├── payments.py   # Payment processing routes
│   │   └── player.py     # Public player routes
│   └── schemas/          # Pydantic request/response models
│       ├── user.py
│       ├── job.py
│       ├── chapter.py
│       ├── outline.py
│       └── payment.py
├── services/              # Business logic services
│   ├── repository_analyzer.py  # Code analysis with tree-sitter
│   ├── outline_generator.py    # Claude-powered outline generation
│   ├── script_generator.py     # Claude-powered script generation
│   ├── audio_synthesizer.py    # TTS audio generation
│   ├── post_processor.py       # Final deliverable creation
│   ├── storage.py              # S3 file operations
│   └── payment.py              # Stripe integration
├── agents/               # Microsoft Agent Framework agent factories
│   └── __init__.py
├── workflows/            # Workflow orchestration scaffolding
│   ├── __init__.py
│   └── audiobook_workflow.py
├── tasks/                 # Agent Framework workflow entry points
│   └── audiobook_tasks.py # Audiobook generation pipeline
├── models/                # SQLAlchemy database models
│   ├── user.py
│   ├── job.py
│   ├── chapter.py
│   ├── outline.py
│   ├── payment.py
│   ├── deliverable.py
│   └── usage_log.py
├── db/                    # Database configuration
│   ├── session.py        # SQLAlchemy session management
│   └── migrations/       # Alembic migrations
├── utils/                 # Utility functions
│   ├── auth.py           # JWT and password utilities
│   └── validators.py     # Input validation
├── main.py               # FastAPI application entry point
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variables template
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- FFmpeg (for audio processing)
- Azure CLI (for local Azure OpenAI authentication)

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

2. **Launch the Microsoft Agent Framework workflow runner** (placeholder):
   ```bash
   # TODO: provide runner command once workflow wiring is complete
   ```

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
   - Merge chapter audio, create cover art, and metadata
   - Prepare deliverables bundle for the player experience

## Environment Variables

See `.env.example` for required environment variables:

- **Database**: `DATABASE_URL`, `CHECKPOINT_DATABASE_URL`
- **Azure OpenAI**: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT_NAME`
- **Other LLM/TTS Providers**: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`
- **Stripe**: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`
- **AWS**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME`, `S3_REGION`
- **Auth**: `JWT_SECRET`, `CLERK_SECRET_KEY`
- **Observability**: `SENTRY_DSN`, `OTEL_EXPORTER_OTLP_ENDPOINT`

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
