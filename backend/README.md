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
- Background job processing with Celery
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
├── tasks/                 # Celery background tasks
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
- Redis 7+
- FFmpeg (for audio processing)

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

7. **Start Redis**:
   ```bash
   redis-server
   ```

### Running the Application

**Development mode:**

1. **Start FastAPI server**:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Celery worker** (in separate terminal):
   ```bash
   celery -A backend.tasks.audiobook_tasks worker --loglevel=info
   ```

3. **Start Celery Flower** (optional monitoring):
   ```bash
   celery -A backend.tasks.audiobook_tasks flower
   ```

**Access the API:**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Flower (Celery monitoring): http://localhost:5555

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

The audiobook generation follows this pipeline:

1. **Repository Analysis** (`analyze_repository` task)
   - Clone repository
   - Parse code with tree-sitter
   - Extract classes, functions, dependencies

2. **Outline Generation** (`generate_outline` task)
   - Use Claude to create chapter structure
   - User can review and modify outline

3. **Script Generation** (`generate_all_scripts` task)
   - Generate narration scripts for each chapter (parallel)
   - Use Claude with code context

4. **Audio Synthesis** (`synthesize_all_audio` task)
   - Convert scripts to speech with TTS (parallel)
   - Upload audio files to S3

5. **Post-Processing** (`post_process_deliverables` task)
   - Combine chapters into full audiobook
   - Generate cover image
   - Create metadata files
   - Upload all deliverables

## Environment Variables

See `.env.example` for required environment variables:

- **Database**: `DATABASE_URL`, `REDIS_URL`
- **API Keys**: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`
- **Stripe**: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- **AWS**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME`
- **Auth**: `JWT_SECRET`
- **Monitoring**: `SENTRY_DSN`

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
- [ ] Implement Celery task logic
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
