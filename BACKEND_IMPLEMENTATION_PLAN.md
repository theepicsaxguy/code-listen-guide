# Codebase Audiobook - Backend Implementation Plan for Launch

## Current State Analysis

### ✅ What You Have (Frontend)
- **Landing page** with Hero, DepthSelector, HowItWorks, SampleShowcase sections
- **Tech stack**: React + TypeScript + Vite + shadcn/ui + TailwindCSS
- **UI components** fully built with shadcn/ui library
- **Form validation** ready (react-hook-form + zod)
- **State management** setup (TanStack Query)
- **Routing** configured (react-router-dom)

### ❌ What's Missing (Critical for Launch)

**Backend Infrastructure**: None exists
**API Endpoints**: None
**Database**: None
**Processing Pipeline**: None
**Payment Integration**: None
**Authentication**: None (required for paid product)
**Job Queue**: None
**File Storage**: None
**Audio Generation**: None

---

## Backend Architecture Overview

### Technology Stack Recommendation

```
Language:           Python 3.11+ (best for ML/AI pipelines)
Framework:          FastAPI (async, fast, automatic docs)
Database:           PostgreSQL (primary) + Redis (caching/queues)
Job Queue:          Celery + Redis
Object Storage:     AWS S3 / Cloudflare R2
LLM Integration:    Anthropic Claude API (script generation)
TTS Integration:    ElevenLabs / OpenAI TTS / Google Cloud TTS
Code Analysis:      tree-sitter (multi-language AST parsing)
Payment:            Stripe
Authentication:     Supabase Auth / Clerk / Auth0
Monitoring:         Sentry (errors) + Datadog/Grafana (metrics)
Deployment:         Railway / Render / AWS ECS
```

**Alternative Stack** (if you prefer .NET):
```
Language:           C# .NET 8
Framework:          ASP.NET Core Web API
Database:           PostgreSQL + Redis
Job Queue:          Hangfire
Everything else:    Same as above
```

I'll proceed with **Python + FastAPI** as it's optimal for AI/ML pipelines.

---

## System Architecture Diagram

```
┌─────────────┐
│   Frontend  │ (React/Vite - Already Built)
│  (Vercel)   │
└──────┬──────┘
       │ HTTPS/REST
       ▼
┌─────────────────────────────────────────────────┐
│            FastAPI Application                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Auth    │  │  Jobs    │  │ Payment  │     │
│  │ Endpoints│  │Endpoints │  │Endpoints │     │
│  └──────────┘  └──────────┘  └──────────┘     │
└────┬─────────────────┬──────────────┬──────────┘
     │                 │              │
     ▼                 ▼              ▼
┌─────────┐      ┌─────────┐   ┌─────────┐
│PostgreSQL│      │  Redis  │   │ Stripe  │
│ (Jobs,  │      │(Queue,  │   │   API   │
│ Users,  │      │ Cache)  │   │         │
│Metadata)│      └────┬────┘   └─────────┘
└─────────┘           │
                      ▼
              ┌───────────────┐
              │ Celery Workers│
              │  (Processing) │
              └───────┬───────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
    ┌───────┐    ┌────────┐   ┌──────┐
    │Claude │    │  TTS   │   │  S3  │
    │  API  │    │  API   │   │Storage│
    └───────┘    └────────┘   └──────┘
```

---

## Database Schema

### Core Tables

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free', -- free, professional, team, enterprise
    subscription_status VARCHAR(50), -- active, canceled, past_due
    credits_remaining INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Jobs table (core entity)
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),

    -- Repository info
    repo_url VARCHAR(500) NOT NULL,
    repo_name VARCHAR(255) NOT NULL,
    repo_owner VARCHAR(255) NOT NULL,
    git_ref VARCHAR(255) DEFAULT 'main',
    repo_size_bytes BIGINT,
    file_count INTEGER,

    -- Configuration
    depth_tier VARCHAR(50) NOT NULL, -- survey, standard, comprehensive
    estimated_duration_minutes INTEGER,
    estimated_chapters INTEGER,

    -- Processing status
    status VARCHAR(50) DEFAULT 'pending', -- pending, analyzing, scripting, synthesizing, post_processing, completed, failed
    current_stage VARCHAR(100),
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    error_message TEXT,

    -- Costs and pricing
    price_paid_cents INTEGER,
    llm_cost_cents INTEGER,
    tts_cost_cents INTEGER,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);

-- Chapters table
CREATE TABLE chapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,

    chapter_number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,

    -- Content coverage
    files_covered TEXT[], -- array of file paths
    topics_covered TEXT[],

    -- Processing
    status VARCHAR(50) DEFAULT 'pending', -- pending, scripting, synthesizing, completed, failed
    script_text TEXT,

    -- Audio
    audio_url VARCHAR(1000),
    audio_duration_seconds INTEGER,
    audio_file_size_bytes BIGINT,

    -- Timestamps
    start_timestamp_ms INTEGER, -- position in full audiobook

    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(job_id, chapter_number)
);

CREATE INDEX idx_chapters_job_id ON chapters(job_id);
CREATE INDEX idx_chapters_status ON chapters(status);

-- Outlines table (approved chapter structure)
CREATE TABLE outlines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,

    outline_data JSONB NOT NULL, -- full chapter structure
    user_approved BOOLEAN DEFAULT FALSE,
    user_modifications JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP
);

-- Payments table
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    job_id UUID REFERENCES jobs(id),

    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_charge_id VARCHAR(255),

    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(50), -- pending, succeeded, failed, refunded

    payment_method_type VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_job_id ON payments(job_id);

-- Deliverables table (track all generated files)
CREATE TABLE deliverables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,

    file_type VARCHAR(50) NOT NULL, -- full_audiobook, chapter_audio, scripts_zip, cover_image, metadata_json, outline_json, code_map_json
    file_url VARCHAR(1000) NOT NULL,
    file_size_bytes BIGINT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_deliverables_job_id ON deliverables(job_id);

-- Usage analytics (for monitoring costs and usage patterns)
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    job_id UUID REFERENCES jobs(id),

    event_type VARCHAR(100) NOT NULL, -- repo_analyzed, script_generated, audio_synthesized, etc.

    tokens_used INTEGER,
    audio_seconds_generated INTEGER,

    cost_cents INTEGER,
    provider VARCHAR(50), -- anthropic, elevenlabs, openai, etc.

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at DESC);
```

---

## API Endpoints Specification

### Authentication Endpoints

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
POST   /api/v1/auth/refresh
```

### Job Endpoints

```
POST   /api/v1/jobs
       Request: { repo_url, depth_tier, git_ref? }
       Response: { job_id, estimated_cost, estimated_time }

GET    /api/v1/jobs
       Query: ?status=completed&limit=10
       Response: { jobs: [...], total, page }

GET    /api/v1/jobs/:job_id
       Response: { job_id, status, progress, chapters: [...], deliverables: [...] }

DELETE /api/v1/jobs/:job_id
       Response: { success: true }
```

### Outline Endpoints

```
POST   /api/v1/jobs/:job_id/outline
       Request: { repo_url, depth_tier }
       Response: { outline_id, chapters: [...], estimated_duration }

PUT    /api/v1/jobs/:job_id/outline/:outline_id
       Request: { chapters: [...], modifications: {...} }
       Response: { outline_id, approved: true }

POST   /api/v1/jobs/:job_id/outline/:outline_id/approve
       Triggers: Payment intent creation + job processing start
       Response: { payment_intent_client_secret }
```

### Payment Endpoints

```
POST   /api/v1/payments/create-intent
       Request: { job_id, amount_cents }
       Response: { payment_intent_id, client_secret }

POST   /api/v1/payments/webhook
       Stripe webhook endpoint (payment confirmation)

GET    /api/v1/payments/history
       Response: { payments: [...] }
```

### Player/Deliverables Endpoints

```
GET    /api/v1/player/:job_id
       Public endpoint (shareable links)
       Response: { job_info, chapters, audio_urls, cover_url }

GET    /api/v1/jobs/:job_id/download/:deliverable_type
       Returns: Pre-signed S3 URL or redirect
```

### Admin Endpoints (Future)

```
GET    /api/v1/admin/jobs
GET    /api/v1/admin/users
GET    /api/v1/admin/analytics
POST   /api/v1/admin/jobs/:job_id/retry
```

---

## Cost Management & Optimization

### Per Audiobook Cost Breakdown

**Standard Depth Example** (React repository, 40 chapters, 8 hours):

**LLM Costs (Claude Sonnet 4):**
- Outline generation: ~50K tokens output = $0.75
- Script generation: 40 chapters × 3K tokens avg = $18.00
- **Total LLM: ~$19**

**TTS Costs (ElevenLabs Turbo):**
- 8 hours = 28,800 seconds
- ElevenLabs pricing: ~$0.30 per 1K characters
- 8 hours ≈ 72K words ≈ 360K characters = $108
- **Total TTS: ~$108**

**Storage & CDN:**
- S3 storage: ~$0.50/month per audiobook
- CDN bandwidth: ~$1 per 100 downloads
- **Total Storage: ~$2 for first 90 days**

**TOTAL COST PER AUDIOBOOK: ~$129**

**Pricing: $49** → **Gross Margin: -62%** ❌

### 🚨 CRITICAL ISSUE: Negative Margins

**The current pricing is NOT viable.** TTS costs alone exceed revenue.

### Solutions to Fix Margins:

#### Option 1: Increase Prices (Recommended)
```
Survey (2-4h):       $29  → Cost ~$40  → Margin: -28%
Standard (6-10h):    $99  → Cost ~$130 → Margin: -24%
Comprehensive (15-25h): $249 → Cost ~$320 → Margin: -22%
```
Still negative! Need more aggressive pricing:

```
Survey (2-4h):       $79  → Cost ~$40  → Margin: +49% ✅
Standard (6-10h):    $199 → Cost ~$130 → Margin: +35% ✅
Comprehensive (15-25h): $499 → Cost ~$320 → Margin: +36% ✅
```

#### Option 2: Reduce TTS Costs
- **Use cheaper TTS**: OpenAI TTS ($15 per 1M chars) = ~$5.40 per 8-hour audiobook
- **New margins with OpenAI TTS**:
  ```
  Standard (8h): $49 price - $24 cost = $25 profit → +51% margin ✅
  ```

#### Option 3: Hybrid Approach
- Use high-quality TTS (ElevenLabs) only for paid tiers
- Use cheaper TTS (OpenAI) for free samples
- Offer voice upgrade as add-on (+$20)

### Recommended Launch Pricing:

```
Survey (2-4 hours):        $69  (OpenAI TTS)
Standard (6-10 hours):     $149 (ElevenLabs TTS)
Comprehensive (15-25 hours): $299 (ElevenLabs TTS)

Cost breakdown (Standard):
- LLM: $19
- TTS (ElevenLabs): $108
- Storage: $2
- Total cost: $129
- Revenue: $149
- Profit: $20
- Margin: 13% (acceptable for launch)
```

---

## Complete Implementation Checklist

### Phase 1: Foundation & Infrastructure
- [ ] Set up FastAPI project structure with all directories
- [ ] Configure PostgreSQL database connection
- [ ] Set up Redis for job queues and caching
- [ ] Implement all database models (SQLAlchemy): User, Job, Chapter, Outline, Payment, Deliverable, UsageLog
- [ ] Create and run Alembic migrations for all tables
- [ ] Set up authentication system (Clerk or Supabase Auth integration)
- [ ] Configure environment variables and secrets management
- [ ] Set up S3 bucket for file storage with proper IAM policies
- [ ] Install and configure Celery with Redis broker
- [ ] Set up Sentry for error monitoring
- [ ] Configure CORS for frontend integration

### Phase 2: Core API Endpoints
- [ ] Implement authentication endpoints (register, login, logout, refresh, me)
- [ ] Create job CRUD endpoints (create, list, get, delete)
- [ ] Build outline endpoints (generate, update, approve)
- [ ] Implement payment endpoints (create-intent, webhook handler)
- [ ] Create public player endpoint for shareable links
- [ ] Add download endpoints with pre-signed S3 URLs
- [ ] Implement rate limiting middleware
- [ ] Add request validation and error handling
- [ ] Create API documentation (auto-generated via FastAPI)

### Phase 3: Repository Analysis Pipeline
- [ ] Implement RepositoryAnalyzer service with git clone functionality
- [ ] Set up tree-sitter parsers for Python, JavaScript, TypeScript, Go, Java, C#
- [ ] Build AST parsing logic to extract classes, functions, imports
- [ ] Create dependency graph builder
- [ ] Implement code structure analyzer (entry points, public APIs)
- [ ] Add repository size validation and limits
- [ ] Create Celery task for repository analysis
- [ ] Add progress tracking and status updates to database
- [ ] Implement cleanup logic for temporary git clones

### Phase 4: Outline Generation
- [ ] Integrate Anthropic Claude API client
- [ ] Implement OutlineGenerator service with prompt engineering
- [ ] Add depth-specific outline generation logic (survey, standard, comprehensive)
- [ ] Create intelligent chapter segmentation algorithm
- [ ] Build chapter duration estimation logic
- [ ] Implement outline storage in database
- [ ] Add user outline customization endpoints
- [ ] Create outline approval workflow
- [ ] Add cost estimation for outline generation

### Phase 5: Script Generation Pipeline
- [ ] Implement ScriptGenerator service with Claude integration
- [ ] Build context window management for large codebases
- [ ] Create chapter-specific prompt templates
- [ ] Implement parallel script generation using Celery groups
- [ ] Add cross-reference tracking between chapters
- [ ] Build script post-processing (formatting, cleanup)
- [ ] Implement script storage in database
- [ ] Add script quality validation
- [ ] Create progress tracking per chapter
- [ ] Add cost tracking for LLM API calls

### Phase 6: Audio Synthesis Pipeline
- [ ] Set up OpenAI TTS API integration (recommended for cost)
- [ ] Implement AudioSynthesizer service
- [ ] Build script chunking logic for API limits
- [ ] Create audio segment generation
- [ ] Implement ffmpeg audio concatenation
- [ ] Add audio normalization and quality control
- [ ] Build parallel audio synthesis using Celery
- [ ] Implement S3 upload for chapter audio files
- [ ] Add audio duration calculation
- [ ] Create progress tracking for synthesis

### Phase 7: Post-Processing & Deliverables
- [ ] Implement PostProcessor service
- [ ] Build full audiobook concatenation with chapter markers
- [ ] Create cover image generator using PIL
- [ ] Implement metadata JSON generation (chapters.json)
- [ ] Build scripts ZIP packaging
- [ ] Add chapter marker embedding in MP3 files
- [ ] Create code map JSON with timestamp-to-code mappings
- [ ] Implement all file uploads to S3
- [ ] Add deliverables tracking in database
- [ ] Build cleanup logic for temporary files

### Phase 8: Payment Integration
- [ ] Set up Stripe account and API keys
- [ ] Implement Stripe payment intent creation
- [ ] Build payment webhook handler for payment confirmation
- [ ] Add payment status tracking in database
- [ ] Create refund handling logic
- [ ] Implement payment receipt generation
- [ ] Add subscription tier management
- [ ] Build credits system for professional/team tiers
- [ ] Create payment history endpoints
- [ ] Add invoice generation

### Phase 9: Celery Task Orchestration
- [ ] Implement main orchestration task (process_audiobook_job)
- [ ] Create task chain for sequential stages
- [ ] Build analyze_repository task
- [ ] Implement generate_outline task
- [ ] Create generate_all_scripts task with parallelization
- [ ] Build generate_chapter_script task
- [ ] Implement synthesize_all_audio task with parallelization
- [ ] Create synthesize_chapter_audio task
- [ ] Build post_process_deliverables task
- [ ] Add error handling and retry logic for all tasks
- [ ] Implement task progress callbacks
- [ ] Add task cancellation support

### Phase 10: Frontend Integration
- [ ] Create API client service in frontend
- [ ] Build repository submission form with validation
- [ ] Implement outline preview component with customization
- [ ] Add Stripe Elements integration for payments
- [ ] Create job progress tracking component with real-time updates
- [ ] Build audio player component with chapter navigation
- [ ] Implement waveform visualization
- [ ] Add download buttons for all deliverables
- [ ] Create shareable link generation and display
- [ ] Build recent jobs list with resume functionality
- [ ] Add error message displays and retry actions
- [ ] Implement loading states and skeletons

### Phase 11: Testing & Quality Assurance
- [ ] Test repository analysis with 20+ diverse repositories (React, Django, Express, Flask, Rails, etc.)
- [ ] Validate script quality and accuracy against actual code
- [ ] Test audio synthesis quality and naturalness
- [ ] Verify payment flow end-to-end
- [ ] Test concurrent job processing (5+ simultaneous jobs)
- [ ] Validate cost tracking accuracy
- [ ] Test error handling and recovery for all failure scenarios
- [ ] Verify S3 file uploads and downloads
- [ ] Test shareable link accessibility
- [ ] Validate chapter navigation and timestamps
- [ ] Load test API endpoints
- [ ] Test rate limiting effectiveness
- [ ] Verify authentication flows

### Phase 12: Monitoring & Operations
- [ ] Set up application performance monitoring (Datadog or similar)
- [ ] Implement cost tracking dashboard
- [ ] Create alerts for high API costs
- [ ] Add job failure notifications
- [ ] Set up database backup automation
- [ ] Implement log aggregation (CloudWatch, Papertrail)
- [ ] Create admin dashboard for job monitoring
- [ ] Add user analytics (PostHog or Mixpanel)
- [ ] Set up uptime monitoring
- [ ] Create health check endpoints
- [ ] Implement metrics collection for all services

### Phase 13: Production Deployment
- [ ] Set up production database (PostgreSQL on Railway/Render)
- [ ] Deploy Redis instance for production
- [ ] Configure production S3 bucket with CDN
- [ ] Deploy FastAPI application to Railway/Render
- [ ] Deploy Celery workers (separate service)
- [ ] Set up environment variables in production
- [ ] Configure custom domain and SSL
- [ ] Deploy frontend to Vercel
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Configure production Stripe webhooks
- [ ] Test production deployment end-to-end
- [ ] Set up database migrations workflow

### Phase 14: Launch Preparation
- [ ] Generate 3-5 sample audiobooks for popular repositories (React, Express, FastAPI)
- [ ] Create case study content for landing page
- [ ] Write API documentation and usage guide
- [ ] Create user onboarding flow
- [ ] Set up customer support email/chat
- [ ] Prepare launch announcement and messaging
- [ ] Create social media assets
- [ ] Set up analytics tracking for conversions
- [ ] Prepare FAQ and troubleshooting guide
- [ ] Test entire user journey from signup to download

### Phase 15: Launch & Monitoring
- [ ] Soft launch to initial users (friends, beta list)
- [ ] Monitor costs in real-time for first 10 jobs
- [ ] Track conversion rates and user feedback
- [ ] Monitor system performance and errors
- [ ] Iterate on script quality based on feedback
- [ ] Adjust pricing if margins are off
- [ ] Fix critical bugs immediately
- [ ] Prepare for scaling (increase worker capacity)
- [ ] Public launch announcement
- [ ] Active monitoring for first 48 hours post-launch

---

## Deployment Architecture

### Recommended: Railway (Simplest)

```yaml
services:
  - name: api
    type: web
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    env:
      - DATABASE_URL: ${{Postgres.DATABASE_URL}}
      - REDIS_URL: ${{Redis.REDIS_URL}}
      - ANTHROPIC_API_KEY: ${{ANTHROPIC_API_KEY}}
      - ELEVENLABS_API_KEY: ${{ELEVENLABS_API_KEY}}
      - STRIPE_SECRET_KEY: ${{STRIPE_SECRET_KEY}}

  - name: worker
    type: worker
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: celery -A tasks.audiobook_tasks worker --loglevel=info
    env:
      - DATABASE_URL: ${{Postgres.DATABASE_URL}}
      - REDIS_URL: ${{Redis.REDIS_URL}}

  - name: postgres
    type: database

  - name: redis
    type: redis
```

### Alternative: Docker Compose (Self-Hosted)

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/audiobook
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  worker:
    build: .
    command: celery -A tasks.audiobook_tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/audiobook
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=audiobook
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## Environment Variables Required

```bash
# .env file

# Database
DATABASE_URL=postgresql://user:password@host:5432/audiobook
REDIS_URL=redis://localhost:6379/0

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxx
ELEVENLABS_API_KEY=xxxxx
OPENAI_API_KEY=sk-xxxxx  # If using OpenAI TTS

# Stripe
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx

# Storage
AWS_ACCESS_KEY_ID=xxxxx
AWS_SECRET_ACCESS_KEY=xxxxx
S3_BUCKET_NAME=codebase-audiobooks
S3_REGION=us-east-1

# Auth (if using Clerk)
CLERK_SECRET_KEY=sk_test_xxxxx
CLERK_PUBLISHABLE_KEY=pk_test_xxxxx

# App
API_BASE_URL=https://api.codebaseaudiobook.com
FRONTEND_URL=https://codebaseaudiobook.com
JWT_SECRET=your-super-secret-jwt-key-change-this

# Monitoring
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

---

## Critical Success Factors

### 1. Script Quality is Everything
The narration quality determines if users get value. You MUST:
- Test with 10+ diverse repositories before launch
- Have humans review scripts for accuracy
- Iterate on prompts until scripts are consistently excellent
- Consider hiring a technical writer to review samples

### 2. Cost Control
- Start with OpenAI TTS ($15/1M chars) not ElevenLabs ($300/1M chars)
- Monitor costs per job in real-time
- Set hard limits on job processing
- Implement automatic job cancellation if costs exceed thresholds

### 3. Processing Speed
- Parallelize everything possible (Celery groups)
- Use Claude API batching where available
- Stream audio generation (don't wait for full script)
- Show partial results to users early

### 4. Error Handling
- Gracefully handle repository parsing failures
- Retry failed chapters (don't fail entire job)
- Preserve partial outputs
- Clear error messages for users

### 5. Security
- Rate limit all endpoints (especially job creation)
- Require authentication for job creation (prevent abuse)
- Validate GitHub URLs (prevent SSRF attacks)
- Sandbox repository analysis (don't execute code)
