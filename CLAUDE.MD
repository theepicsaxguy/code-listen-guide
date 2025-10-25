# CLAUDE.MD - AI Assistant Guide for Codebase Audiobook

> **Last Updated**: October 25, 2025
> **Project Status**: MVP in Development - Frontend Complete, Backend Services TODO
> **Architecture**: Microsoft Agent Framework (Python) + React 19 + FastAPI

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Quick Start for AI Assistants](#quick-start-for-ai-assistants)
3. [Architecture & Implementation Status](#architecture--implementation-status)
4. [Development Guidelines](#development-guidelines)
5. [Microsoft Agent Framework Integration](#microsoft-agent-framework-integration)
6. [Frontend Architecture](#frontend-architecture)
7. [Backend Architecture](#backend-architecture)
8. [Critical Implementation Gaps](#critical-implementation-gaps)
9. [Testing Strategy](#testing-strategy)
10. [Deployment & CI/CD](#deployment--cicd)
11. [Common Tasks & Patterns](#common-tasks--patterns)
12. [Troubleshooting](#troubleshooting)

---

## Project Overview

### What We're Building

**Codebase Audiobook** transforms any GitHub repository into a professionally narrated audiobook. Developers can listen to comprehensive code walkthroughs during commutes, workouts, or any time screen interaction is impossible.

### Core Value Proposition

- **Audio-first code learning** - Consume complex codebases hands-free
- **Multi-agent orchestration** - Microsoft Agent Framework coordinates specialized AI agents
- **Complete coverage** - Every function, pattern, and architectural decision explained
- **Professional quality** - Broadcast-quality audio with chapter markers and metadata

### Target Users

1. Senior engineers onboarding to complex codebases
2. Technical leads evaluating open-source dependencies
3. Developers learning from flagship projects (React, Django, Kubernetes)
4. Computer science students studying real-world implementations

### Business Model

- **Survey tier** (2-4 hours): $19
- **Standard tier** (6-10 hours): $49
- **Comprehensive tier** (15-25 hours): $99
- **Subscription plans** for teams and enterprises

---

## Quick Start for AI Assistants

### First-Time Contributors: Read This First

1. **Read `README.md`** - User-facing documentation with setup instructions
2. **Read `Plan.md`** - Investor specification with vision and architecture (ASPIRATIONAL)
3. **Read `BACKEND_IMPLEMENTATION_PLAN.md`** - Detailed technical architecture (PLANNED, NOT ALL IMPLEMENTED)
4. **Search for `TODO:`** - Find specific implementation gaps throughout the codebase
5. **Check this file's [Critical Implementation Gaps](#critical-implementation-gaps)** section

### IMPORTANT: What's Real vs. Aspirational

| Document | Status | Use Case |
|----------|--------|----------|
| `README.md` | ✅ Accurate | Setup and development workflow |
| `Plan.md` | 📋 Vision | Understand goals, NOT current state |
| `BACKEND_IMPLEMENTATION_PLAN.md` | 📋 Blueprint | Architecture guide, many TODOs remain |
| `plans/*.md` | 📋 Future | Roadmap items (Docling, launch strategy) |
| This file (`CLAUDE.MD`) | ✅ Reality Check | Current implementation status |

### Key Principle for AI Assistants

> **When making changes, ALWAYS verify current implementation status before assuming functionality exists. Most backend services are scaffolded but not implemented.**

---

## Architecture & Implementation Status

### System Components Overview

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  ✅ Complete (95%)                                       │
│  - 8 routes, 76 TypeScript files                        │
│  - 60+ shadcn/ui components                             │
│  - Full type safety with Zod validation                 │
│  - React Query for data fetching                        │
│  - Auth context and protected routes                    │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/WebSocket
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│  ~ Partial (40%)                                         │
│  - ✅ Routes defined, schemas created                   │
│  - ✅ Database models with all fields                   │
│  - ✅ CORS, middleware, exception handling              │
│  - ❌ Service implementations (mostly TODO)             │
│  - ❌ Agent logic (scaffolded only)                     │
└────────────────────┬────────────────────────────────────┘
                     │
       ┌─────────────┼─────────────┬──────────────┐
       ▼             ▼             ▼              ▼
┌─────────┐   ┌──────────┐  ┌──────────┐  ┌──────────┐
│Microsoft│   │PostgreSQL│  │  AWS S3  │  │  Stripe  │
│  Agent  │   │          │  │          │  │          │
│Framework│   │ ✅ Models│  │❌ Not    │  │❌ Not    │
│         │   │ ❌ No    │  │integrated│  │integrated│
│~ Partial│   │migrations│  │          │  │          │
│  (30%)  │   │          │  │          │  │          │
└─────────┘   └──────────┘  └──────────┘  └──────────┘
```

### Implementation Status by Component

#### ✅ Complete (Ready to Use)

1. **Frontend UI** (95%)
   - All page layouts designed and styled
   - Form validation with react-hook-form + Zod
   - Responsive design with Tailwind CSS
   - Dark mode support
   - Icon system (Lucide React)
   - Toast notifications (Sonner)

2. **Frontend Infrastructure** (100%)
   - Vite build system with React SWC
   - TypeScript with strict mode
   - ESLint with React hooks rules
   - Path aliases (`@/*` → `src/*`)
   - Environment variable system

3. **Backend Infrastructure** (100%)
   - FastAPI app with CORS
   - Request/response logging middleware
   - Global exception handlers
   - Health check endpoint
   - OpenTelemetry instrumentation (optional)
   - Pydantic settings with .env support

4. **Type System** (100%)
   - Complete TypeScript interfaces in `src/lib/types.ts`
   - Pydantic schemas in `backend/api/schemas/`
   - SQLAlchemy models with all fields defined

#### ~ Partial (Needs Work)

1. **Database Layer** (80%)
   - ✅ All models defined with fields
   - ✅ Relationships mapped (but commented out with TODOs)
   - ❌ No Alembic migrations configured
   - ❌ No seed data

2. **API Routes** (40%)
   - ✅ All endpoints defined
   - ✅ Request/response schemas created
   - ~ Basic CRUD operations work (jobs list/create)
   - ❌ Workflow integration missing
   - ❌ Real-time updates (WebSocket) not implemented

3. **Microsoft Agent Framework** (30%)
   - ✅ Package installed (`agent-framework==1.0.0b251016`)
   - ✅ Workflow structure defined
   - ✅ Agent definitions created
   - ❌ Tool implementations mostly empty
   - ❌ Agent logic incomplete
   - ❌ Checkpointing not wired up

#### ❌ Not Implemented (Critical Gaps)

1. **Repository Analysis Service** (10%)
   - File: `backend/services/repository_analyzer.py`
   - Status: Skeleton with TODO comments
   - Needs: Tree-sitter integration, dependency graph extraction

2. **Outline Generation Service** (0%)
   - File: `backend/services/outline_generator.py`
   - Status: Empty, all TODO
   - Needs: Claude API integration, semantic clustering

3. **Script Generation Service** (0%)
   - File: `backend/services/script_generator.py`
   - Status: Empty, all TODO
   - Needs: Narrative generation, context management

4. **Audio Synthesis Service** (0%)
   - File: `backend/services/audio_synthesizer.py`
   - Status: Empty, all TODO
   - Needs: TTS integration (ElevenLabs/OpenAI), audio processing

5. **Post-Processing Service** (0%)
   - File: `backend/services/post_processor.py`
   - Status: Empty, all TODO
   - Needs: Audio merging, metadata creation, S3 upload

6. **Payment Integration** (0%)
   - File: `backend/services/payment.py`
   - Status: Empty, all TODO
   - Needs: Stripe payment intents, webhook handling

7. **Storage Service** (0%)
   - File: `backend/services/storage.py`
   - Status: Empty, all TODO
   - Needs: AWS S3 upload/download/URL generation

---

## Development Guidelines

### Code Style & Standards

#### Frontend (TypeScript/React)

```typescript
// ✅ GOOD: Use types from lib/types.ts
import { Job, Chapter, OutlineData } from '@/lib/types';

const MyComponent = ({ job }: { job: Job }) => {
  // ...
};

// ✅ GOOD: Use API client methods
import { apiClient } from '@/lib/api';
const jobs = await apiClient.getJobs({ status: 'completed' });

// ✅ GOOD: Use React Query for data fetching
const { data, isLoading } = useQuery({
  queryKey: ['jobs', status],
  queryFn: () => apiClient.getJobs({ status })
});

// ❌ BAD: Direct fetch calls
const response = await fetch('/api/v1/jobs');
```

#### Backend (Python/FastAPI)

```python
# ✅ GOOD: Use dependency injection
from backend.db.session import get_db
from sqlalchemy.orm import Session

@router.get("/jobs")
async def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()

# ✅ GOOD: Use Pydantic schemas for validation
from backend.api.schemas.job import JobCreate, JobResponse

@router.post("/jobs", response_model=JobResponse)
async def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    # ...

# ✅ GOOD: Log important events
import logging
logger = logging.getLogger(__name__)
logger.info(f"Starting workflow for job {job_id}")

# ✅ GOOD: Handle errors gracefully
try:
    result = await some_operation()
except SomeSpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))

# ❌ BAD: Bare exception handlers
except Exception:
    pass
```

### File Organization Conventions

#### Frontend Structure

```
src/
├── pages/           # Route components (one per URL)
├── components/      # Reusable UI components
│   ├── ui/         # shadcn/ui primitives (auto-generated, rarely edit)
│   └── *.tsx       # Custom components (Hero, DepthSelector, etc.)
├── lib/            # Core utilities and types
│   ├── types.ts    # ALL TypeScript interfaces (single source of truth)
│   ├── api.ts      # API client class
│   ├── utils.ts    # Helper functions
│   └── queryClient.ts
├── contexts/       # React context providers
├── hooks/          # Custom React hooks
└── App.tsx         # Router configuration
```

**When adding a new page:**
1. Create component in `src/pages/MyNewPage.tsx`
2. Add type to `src/lib/types.ts` if needed
3. Add route to `src/App.tsx`
4. Add navigation link in appropriate component

#### Backend Structure

```
backend/
├── main.py              # FastAPI app initialization
├── config.py            # Environment-based settings
├── api/
│   ├── routes/         # Endpoint handlers (auth, jobs, outlines, etc.)
│   └── schemas/        # Pydantic request/response models
├── models/             # SQLAlchemy database models
├── services/           # Business logic (repository_analyzer, etc.)
├── agents/             # Microsoft Agent Framework agents
├── workflows/          # Workflow orchestration
├── tools/              # Agent tools (functions agents can call)
├── db/
│   ├── session.py      # Database connection
│   └── migrations/     # Alembic (not yet configured)
├── utils/              # Helpers (auth, validators, checkpointing)
└── tests/              # Pytest test files
```

**When adding a new endpoint:**
1. Create route handler in `backend/api/routes/my_route.py`
2. Define schemas in `backend/api/schemas/my_route.py`
3. Implement service logic in `backend/services/my_service.py`
4. Update database model in `backend/models/` if needed
5. Register router in `backend/main.py`

### Environment Variables

#### Frontend (`.env` in root)

```bash
# API endpoint (required)
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

#### Backend (`backend/.env`)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/audiobook
# or for development:
DATABASE_URL=sqlite:///./audiobook.db

# LLM APIs
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=sk-...
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# TTS
ELEVENLABS_API_KEY=...

# Storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=codebase-audiobooks
S3_REGION=us-east-1

# Payments
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Auth
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# Optional: Observability
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
SENTRY_DSN=https://...
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/outline-generation

# Make changes, commit often
git add backend/services/outline_generator.py
git commit -m "feat: implement Claude-based outline generation"

# Push and create PR
git push origin feature/outline-generation
```

**Commit Message Convention:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code restructuring without behavior change
- `test:` - Adding or updating tests
- `chore:` - Build tasks, dependency updates

---

## Microsoft Agent Framework Integration

### Overview

This project uses **Microsoft Agent Framework** (released October 1, 2025) to orchestrate a multi-agent workflow. This is the unified successor to AutoGen and Semantic Kernel.

**Why Agent Framework?**
- Enterprise-grade reliability with production-ready runtime
- Built-in checkpointing for long-running workflows
- Graph-based workflows with type safety
- Native Azure integration
- OpenTelemetry observability out of the box

### Current Implementation Status

**Installed Version:** `agent-framework==1.0.0b251016` (Beta from October 16, 2025)

**What's Implemented:**
- ✅ Package installed and importable
- ✅ Workflow structure defined in `backend/workflows/audiobook_workflow.py`
- ✅ Agent definitions in `backend/agents/`
- ✅ Tool stubs in `backend/tools/`

**What's Missing:**
- ❌ Actual tool implementations (all TODO)
- ❌ Agent prompts and configurations need refinement
- ❌ Workflow checkpointing not wired to PostgreSQL
- ❌ Real LLM calls (Azure OpenAI client created but not used)
- ❌ Error handling and retry logic

### Agent Architecture

The audiobook generation workflow uses 6 specialized agents:

```python
# Sequential stages
1. RepositoryAnalyzer → Clones repo, parses code structure
2. OutlineGenerator → Creates chapter outline using Claude
3. HumanApproval → Pauses for user review (human-in-the-loop)

# Concurrent stages
4. ScriptWriter (pool) → Multiple agents generate scripts in parallel
5. AudioProducer (pool) → Multiple agents synthesize audio

# Final stage
6. PostProcessor → Merges audio, creates deliverables
```

### Workflow Execution Pattern

```python
# Location: backend/workflows/audiobook_workflow.py

from agent_framework import WorkflowBuilder, SequentialBuilder, ConcurrentBuilder

class AudiobookWorkflow:
    async def execute(self, job_id: str, repo_url: str):
        # Stage 1: Analysis (sequential)
        analysis = await self.analyzer_agent.run(repo_url)

        # Stage 2: Outline (sequential)
        outline = await self.outline_agent.run(analysis)

        # Stage 3: Human approval (pause workflow)
        approved_outline = await self.wait_for_approval(outline)

        # Stage 4: Script generation (concurrent)
        scripts = await asyncio.gather(*[
            script_agent.run(chapter)
            for chapter in approved_outline.chapters
        ])

        # Stage 5: Audio synthesis (batched concurrent)
        audio_files = await self.synthesize_in_batches(scripts)

        # Stage 6: Post-processing (sequential)
        deliverables = await self.postprocess_agent.run(audio_files)

        return deliverables
```

### Implementing an Agent

**Example: Outline Generator Agent**

```python
# File: backend/agents/outline_agent.py

from agent_framework import Agent
from backend.config import get_settings

async def create_outline_agent(chat_client):
    """Create an agent that generates audiobook chapter outlines."""

    settings = get_settings()

    return Agent(
        name="OutlineGenerator",
        instructions="""
        You are an expert technical writer designing audiobook outlines.

        Given a code repository analysis, create a comprehensive chapter structure:
        - Group related files into thematic chapters
        - Estimate duration per chapter (aim for 15-30 minute chapters)
        - Define clear learning objectives for each chapter
        - Ensure logical narrative flow

        Output JSON with:
        {
          "chapters": [
            {
              "number": 1,
              "title": "Authentication Middleware",
              "description": "JWT validation and user context",
              "files_covered": ["src/auth/*.ts"],
              "topics": ["JWT validation", "User sessions"],
              "estimated_duration_minutes": 20,
              "learning_objectives": ["Understand auth flow", "..."]
            }
          ],
          "total_estimated_duration_minutes": 180,
          "total_chapters": 8
        }
        """,
        chat_client=chat_client,
        # Tools can be added here when needed
        tools=[]
    )
```

### Implementing a Tool

**Example: Git Clone Tool**

```python
# File: backend/tools/git_tools.py

from agent_framework.tools import FunctionTool
import git
import tempfile
import shutil

def clone_repository(repo_url: str, git_ref: str = "main") -> dict:
    """
    Clone a GitHub repository to a temporary directory.

    Args:
        repo_url: GitHub repository URL (https://github.com/user/repo)
        git_ref: Branch, tag, or commit hash (default: main)

    Returns:
        {
            "local_path": "/tmp/repo_xyz",
            "commit_hash": "abc123...",
            "files_count": 42
        }
    """
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="audiobook_repo_")

    try:
        # Clone repository
        repo = git.Repo.clone_from(repo_url, temp_dir)

        # Checkout specified ref
        repo.git.checkout(git_ref)

        # Count files
        files_count = sum(1 for _ in Path(temp_dir).rglob('*') if _.is_file())

        return {
            "local_path": temp_dir,
            "commit_hash": repo.head.commit.hexsha,
            "files_count": files_count,
            "branch": git_ref
        }
    except Exception as e:
        # Cleanup on error
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ValueError(f"Failed to clone repository: {str(e)}")

# Wrap as FunctionTool for Agent Framework
clone_tool = FunctionTool(
    name="clone_repository",
    description="Clone a GitHub repository to analyze its code",
    func=clone_repository
)
```

### Checkpointing Strategy

Checkpoints allow workflows to resume after failures without re-running expensive operations (like LLM calls).

**Implementation Location:** `backend/utils/checkpointing.py`

```python
# TODO: Current implementation is a skeleton
# Need to:
# 1. Create PostgreSQL checkpoint storage class
# 2. Serialize workflow state as JSON
# 3. Save checkpoint after each stage
# 4. Implement resume logic

from agent_framework.workflows import CheckpointStore

class PostgreSQLCheckpointStore(CheckpointStore):
    async def save_checkpoint(self, workflow_id: str, stage: str, data: dict):
        """Save workflow state to database."""
        # TODO: Implement
        pass

    async def load_checkpoint(self, workflow_id: str) -> dict | None:
        """Load latest checkpoint for workflow."""
        # TODO: Implement
        pass
```

### Cost Tracking

Track LLM and TTS costs per job in the `usage_logs` table.

```python
# Location: backend/models/usage_log.py

class UsageLog(Base):
    job_id = Column(UUID, ForeignKey("jobs.id"))
    service_type = Column(String)  # "azure_openai", "anthropic", "elevenlabs"
    tokens_used = Column(Integer)
    cost_cents = Column(Integer)
```

**Update costs after each agent run:**

```python
# In workflow
result = await agent.run(...)

# Track usage
usage_log = UsageLog(
    job_id=job_id,
    service_type="anthropic",
    tokens_used=result.usage.total_tokens,
    cost_cents=calculate_cost(result.usage)
)
db.add(usage_log)
```

### Reference Implementation

**File:** `samples/microsoft-agent-framework-cab263a3ceac6346.txt`

This 24,000-line file contains reference examples from Microsoft's Agent Framework. Search it for patterns:

```bash
# Find checkpoint examples
grep -n "checkpoint" samples/microsoft-agent-framework-*.txt

# Find concurrent execution examples
grep -n "concurrent" samples/microsoft-agent-framework-*.txt
```

---

## Frontend Architecture

### Routing & Navigation

**Router Configuration:** `src/App.tsx`

```typescript
// Public routes
/ → Index (landing page)
/why-we-exist → WhyWeExist (mission statement)
/auth → Auth (login/register)

// Protected routes (redirect to /auth if not logged in)
/dashboard → Dashboard (user's jobs)
/submit → Submit (create new audiobook)
/jobs/:jobId → JobDetails (job status)
/jobs/:jobId/outline → OutlinePreview (review and approve)
/player/:jobId → Player (audiobook player - PUBLIC but needs job data)

// Fallback
/* → NotFound (404 page)
```

**Protected Route Pattern:**

```typescript
// Location: src/App.tsx
import { useAuth } from '@/contexts/AuthContext';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/auth" />;

  return <>{children}</>;
};

// Usage
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />
```

### State Management

**Authentication State:** `src/contexts/AuthContext.tsx`

```typescript
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

// Usage in components
const { user, login, logout } = useAuth();
```

**API Data State:** React Query (TanStack Query)

```typescript
// Location: src/lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      retry: 1,
    }
  }
});

// Usage in components
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

const { data: jobs, isLoading, error } = useQuery({
  queryKey: ['jobs', { status: 'completed' }],
  queryFn: () => apiClient.getJobs({ status: 'completed' })
});
```

### Type System

**Location:** `src/lib/types.ts` (single source of truth)

```typescript
// Core domain types
export interface User {
  id: string;
  email: string;
  name: string;
  subscription_tier: 'free' | 'professional' | 'team' | 'enterprise';
  credits_remaining: number;
}

export interface Job {
  id: string;
  user_id: string;
  repo_url: string;
  repo_name: string;
  repo_owner: string;
  git_ref: string;
  depth_tier: 'survey' | 'standard' | 'comprehensive';
  status: 'pending' | 'analyzing' | 'scripting' | 'synthesizing' | 'post_processing' | 'completed' | 'failed';
  progress_percentage: number;
  current_stage: string;
  estimated_duration_minutes: number | null;
  estimated_chapters: number | null;
  price_paid_cents: number;
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  id: string;
  job_id: string;
  chapter_number: number;
  title: string;
  description: string;
  files_covered: string[];
  topics_covered: string[];
  status: 'pending' | 'scripting' | 'synthesizing' | 'completed' | 'failed';
  script_text: string | null;
  audio_url: string | null;
  audio_duration_seconds: number | null;
}

export interface OutlineData {
  chapters: ChapterOutline[];
  total_estimated_duration_minutes: number;
  total_chapters: number;
}

export interface ChapterOutline {
  number: number;
  title: string;
  description: string;
  files_covered: string[];
  topics_covered: string[];
  estimated_duration_minutes: number;
  learning_objectives: string[];
}
```

**Always import types from this file, never define inline:**

```typescript
// ✅ GOOD
import { Job, Chapter } from '@/lib/types';

// ❌ BAD
interface Job { ... } // Don't duplicate
```

### API Client

**Location:** `src/lib/api.ts`

```typescript
class APIClient {
  private baseURL: string;
  private authToken: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.authToken = localStorage.getItem('auth_token');
  }

  // Auth methods
  async login(email: string, password: string): Promise<{ access_token: string; user: User }>;
  async register(email: string, password: string, name: string): Promise<{ access_token: string; user: User }>;
  async getMe(): Promise<User>;

  // Job methods
  async createJob(data: CreateJobRequest): Promise<Job>;
  async getJobs(params?: { status?: string; limit?: number; page?: number }): Promise<Job[]>;
  async getJob(jobId: string): Promise<Job>;
  async deleteJob(jobId: string): Promise<void>;

  // Outline methods
  async generateOutline(jobId: string, data: GenerateOutlineRequest): Promise<OutlineData>;
  async approveOutline(jobId: string, outlineId: string): Promise<void>;

  // Payment methods
  async createPaymentIntent(jobId: string, amount: number): Promise<{ client_secret: string }>;

  // Player methods
  async getPlayerData(jobId: string): Promise<PlayerData>;
}

export const apiClient = new APIClient(
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
);
```

**All API calls should go through this client:**

```typescript
// ✅ GOOD
const job = await apiClient.createJob({ repo_url, depth_tier });

// ❌ BAD
const response = await fetch('/api/v1/jobs', { ... });
```

### UI Components

**shadcn/ui Components** (`src/components/ui/`)

60+ pre-built components available. These are auto-generated - rarely edit directly.

Common components:
- `Button`, `Input`, `Label`, `Textarea`
- `Card`, `Badge`, `Avatar`, `Progress`
- `Dialog`, `Sheet`, `Popover`, `Tooltip`
- `Select`, `Checkbox`, `RadioGroup`, `Switch`
- `Table`, `Tabs`, `Accordion`, `Carousel`

**Custom Components** (`src/components/`)

- `Hero.tsx` - Landing page hero with gradient
- `HowItWorks.tsx` - Process explanation section
- `SampleShowcase.tsx` - Feature showcase
- `Footer.tsx` - Site footer
- `DepthSelector.tsx` - Audiobook tier picker
- `MarketValidation.tsx` - Market data visualization

**Adding a new component:**

```bash
# Use shadcn CLI to add primitives
npx shadcn@latest add [component-name]

# Create custom component manually
touch src/components/MyComponent.tsx
```

### Styling System

**Tailwind CSS** with custom theme in `tailwind.config.ts`

```typescript
// Custom colors
colors: {
  border: "hsl(var(--border))",
  background: "hsl(var(--background))",
  foreground: "hsl(var(--foreground))",
  primary: { ... },
  secondary: { ... },
  // ... full theme in config
}

// Usage
<div className="bg-background text-foreground p-4 rounded-lg">
  <Button className="bg-primary text-primary-foreground">
    Click me
  </Button>
</div>
```

**Dark mode:**

```typescript
// Controlled by next-themes
import { useTheme } from 'next-themes';

const { theme, setTheme } = useTheme();
setTheme('dark'); // or 'light' or 'system'
```

---

## Backend Architecture

### Request/Response Flow

```
1. HTTP Request
   ↓
2. FastAPI route handler (backend/api/routes/*.py)
   ↓
3. Pydantic schema validation (backend/api/schemas/*.py)
   ↓
4. Service layer (backend/services/*.py)
   ↓
5. Database operations (backend/models/*.py)
   ↓
6. Response serialization
   ↓
7. HTTP Response
```

### Database Models

**Location:** `backend/models/`

**Current Status:** All models defined with fields, relationships commented out with TODOs.

**Models:**
- `user.py` - User accounts with subscription tiers
- `job.py` - Audiobook generation jobs
- `chapter.py` - Individual chapters within a job
- `outline.py` - User-reviewable chapter outlines
- `deliverable.py` - S3 file references
- `payment.py` - Stripe payment records
- `usage_log.py` - Cost tracking per job
- `workflow_checkpoint.py` - Agent Framework state persistence

**Example: Job Model**

```python
# File: backend/models/job.py

from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.db.base import Base
import uuid
import enum

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    WAITING_APPROVAL = "waiting_approval"
    SCRIPTING = "scripting"
    SYNTHESIZING = "synthesizing"
    POST_PROCESSING = "post_processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Repository info
    repo_url = Column(String, nullable=False)
    repo_name = Column(String, nullable=False)
    repo_owner = Column(String, nullable=False)
    git_ref = Column(String, default="main")

    # Configuration
    depth_tier = Column(String, nullable=False)  # survey, standard, comprehensive

    # Status tracking
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    progress_percentage = Column(Float, default=0.0)
    current_stage = Column(String)

    # Estimates
    estimated_duration_minutes = Column(Integer)
    estimated_chapters = Column(Integer)

    # Costs
    price_paid_cents = Column(Integer, default=0)
    llm_cost_cents = Column(Integer, default=0)
    tts_cost_cents = Column(Integer, default=0)

    # Metadata
    metadata = Column(JSONB)
    error_message = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (TODO: Uncomment when ready to use)
    # user = relationship("User", back_populates="jobs")
    # chapters = relationship("Chapter", back_populates="job", cascade="all, delete-orphan")
    # outlines = relationship("Outline", back_populates="job")
```

### Database Session Management

**Location:** `backend/db/session.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for FastAPI routes to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Usage in routes:**

```python
from backend.db.session import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

@router.get("/jobs")
async def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return jobs
```

### Pydantic Schemas

**Location:** `backend/api/schemas/`

These define request/response formats and validation rules.

```python
# File: backend/api/schemas/job.py

from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, List
from datetime import datetime

class JobCreate(BaseModel):
    repo_url: HttpUrl
    depth_tier: str  # survey, standard, comprehensive
    git_ref: str = "main"

    @field_validator('depth_tier')
    def validate_depth_tier(cls, v):
        if v not in ['survey', 'standard', 'comprehensive']:
            raise ValueError('Invalid depth tier')
        return v

class JobResponse(BaseModel):
    id: str
    user_id: str
    repo_url: str
    repo_name: str
    repo_owner: str
    git_ref: str
    depth_tier: str
    status: str
    progress_percentage: float
    current_stage: Optional[str]
    estimated_duration_minutes: Optional[int]
    estimated_chapters: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # For SQLAlchemy model conversion
```

### API Routes

**Location:** `backend/api/routes/`

**Route Files:**
- `auth.py` - Authentication endpoints
- `jobs.py` - Job CRUD operations
- `outlines.py` - Outline generation and approval
- `payments.py` - Payment processing
- `player.py` - Public player data
- `webhooks.py` - External webhooks (Stripe, etc.)

**Example: Jobs Route**

```python
# File: backend/api/routes/jobs.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.api.schemas.job import JobCreate, JobResponse
from backend.models.job import Job
from typing import List, Optional

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # TODO: Implement auth dependency
):
    """
    Create a new audiobook generation job.

    TODO:
    - Validate repository URL is accessible
    - Calculate price based on depth tier
    - Trigger workflow execution
    - Emit WebSocket event for real-time updates
    """
    # Extract repo name and owner from URL
    # TODO: Implement proper GitHub URL parsing
    repo_name = "placeholder"
    repo_owner = "placeholder"

    job = Job(
        user_id=current_user.id,
        repo_url=str(job_data.repo_url),
        repo_name=repo_name,
        repo_owner=repo_owner,
        git_ref=job_data.git_ref,
        depth_tier=job_data.depth_tier,
        status="pending"
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # TODO: Trigger workflow
    # await trigger_audiobook_workflow(job.id)

    return job

@router.get("", response_model=List[JobResponse])
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List user's jobs with optional filtering."""
    query = db.query(Job).filter(Job.user_id == current_user.id)

    if status:
        query = query.filter(Job.status == status)

    offset = (page - 1) * limit
    jobs = query.offset(offset).limit(limit).all()

    return jobs
```

### Service Layer

**Location:** `backend/services/`

This is where business logic lives. **Most services are currently TODO.**

**Service Files:**
- `repository_analyzer.py` - Clone repo, parse code structure
- `outline_generator.py` - Generate chapter outlines
- `script_generator.py` - Write narration scripts
- `audio_synthesizer.py` - Text-to-speech and audio processing
- `post_processor.py` - Merge audio, create deliverables
- `payment.py` - Stripe integration
- `storage.py` - AWS S3 operations

**Example Service Implementation Pattern:**

```python
# File: backend/services/outline_generator.py

from typing import Dict, List
from backend.agents.outline_agent import create_outline_agent
from backend.config import get_settings
import logging

logger = logging.getLogger(__name__)

async def generate_outline(
    analysis_data: Dict,
    depth_tier: str,
    job_id: str
) -> Dict:
    """
    Generate audiobook chapter outline from repository analysis.

    Args:
        analysis_data: Repository structure from analyzer
        depth_tier: survey, standard, or comprehensive
        job_id: Job ID for tracking

    Returns:
        Outline data with chapters, durations, topics

    TODO:
    - Create Anthropic client with Claude API
    - Pass analysis to outline agent
    - Implement semantic clustering of related files
    - Calculate realistic chapter durations
    - Handle errors gracefully
    """
    logger.info(f"Generating outline for job {job_id} with tier {depth_tier}")

    settings = get_settings()

    # TODO: Initialize Claude client
    # from anthropic import AsyncAnthropic
    # client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    # TODO: Create outline agent
    # agent = await create_outline_agent(client)

    # TODO: Run agent with analysis data
    # result = await agent.run(analysis_data)

    # TODO: Parse and validate result
    # outline = parse_outline(result)

    # Placeholder return
    return {
        "chapters": [],
        "total_estimated_duration_minutes": 0,
        "total_chapters": 0
    }
```

### Configuration System

**Location:** `backend/config.py`

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./audiobook.db"

    # LLM APIs
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4o"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # TTS
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # Default voice

    # Storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "codebase-audiobooks"
    S3_REGION: str = "us-east-1"

    # Payments
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Auth
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Observability (optional)
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    SENTRY_DSN: str = ""

    class Config:
        env_file = "backend/.env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
```

**Usage:**

```python
from backend.config import get_settings

settings = get_settings()
api_key = settings.ANTHROPIC_API_KEY
```

---

## Critical Implementation Gaps

### High-Priority Services (Blocking MVP)

#### 1. Repository Analyzer Service

**File:** `backend/services/repository_analyzer.py`
**Status:** 10% complete (skeleton only)
**Dependencies:** `tree-sitter`, `GitPython`

**What needs to be done:**
1. Implement Git clone functionality (using `GitPython`)
2. Walk repository file tree
3. Parse code files with tree-sitter for each language:
   - Python: `tree-sitter-python`
   - JavaScript/TypeScript: `tree-sitter-javascript`, `tree-sitter-typescript`
   - Add more languages as needed
4. Extract:
   - Function/class definitions
   - Import statements and dependencies
   - Comments and docstrings
   - File structure
5. Build dependency graph
6. Return structured JSON for outline agent

**Reference:**
- Tree-sitter docs: https://tree-sitter.github.io/tree-sitter/
- Example in `backend/tools/code_parser_tools.py` (currently TODO)

**Estimated effort:** 2-3 days

---

#### 2. Outline Generator Service

**File:** `backend/services/outline_generator.py`
**Status:** 0% complete (TODO)
**Dependencies:** `anthropic` (Claude API)

**What needs to be done:**
1. Initialize Anthropic Claude client
2. Design prompt for outline generation:
   - Input: Repository analysis JSON
   - Output: Structured chapter outline
   - Context: Depth tier (survey/standard/comprehensive)
3. Implement semantic clustering to group related files
4. Calculate realistic chapter durations
5. Define learning objectives per chapter
6. Return outline JSON matching `OutlineData` schema
7. Save outline to database

**Key considerations:**
- Survey tier: 2-4 hours total, focus on architecture and public APIs
- Standard tier: 6-10 hours, all public interfaces + key private functions
- Comprehensive tier: 15-25 hours, every function and implementation detail

**Estimated effort:** 2-3 days

---

#### 3. Script Generator Service

**File:** `backend/services/script_generator.py`
**Status:** 0% complete (TODO)
**Dependencies:** `anthropic` or `azure-ai-openai`

**What needs to be done:**
1. Initialize LLM client (Claude or Azure OpenAI)
2. Design prompt for narration script generation:
   - Input: Chapter outline + code context
   - Output: Engaging technical narration (not code dumping)
   - Tone: Educational, conversational, professional
3. Implement context management for cross-chapter references
4. Generate scripts for each chapter (can run in parallel)
5. Save scripts to database as they complete
6. Track token usage and costs

**Key considerations:**
- Scripts should explain *why* code works this way, not just *what* it does
- Include forward/backward references between chapters
- Aim for 15-30 minute chapters (2000-4000 words)
- Handle edge cases (generated code, minified code, etc.)

**Estimated effort:** 3-4 days

---

#### 4. Audio Synthesizer Service

**File:** `backend/services/audio_synthesizer.py`
**Status:** 0% complete (TODO)
**Dependencies:** `elevenlabs` or `openai`, `pydub`, `ffmpeg`

**What needs to be done:**
1. Initialize TTS client (ElevenLabs or OpenAI TTS)
2. Convert script text to audio:
   - Split long scripts into chunks (TTS has character limits)
   - Synthesize each chunk
   - Concatenate chunks into single chapter audio
3. Audio processing:
   - Normalize volume levels
   - Add silence between sections
   - Embed chapter markers
   - Export as MP3
4. Upload to S3 (call storage service)
5. Save audio metadata to database (URL, duration)
6. Track TTS costs

**Key considerations:**
- ElevenLabs: 2500 chars/request, costs ~$0.30/1000 chars
- OpenAI TTS: Lower cost but less natural quality
- Standard chapter: ~3000 words = ~20 minutes audio
- Batch processing to avoid rate limits

**Estimated effort:** 3-4 days

---

#### 5. Post-Processor Service

**File:** `backend/services/post_processor.py`
**Status:** 0% complete (TODO)
**Dependencies:** `pydub`, `ffmpeg`, storage service

**What needs to be done:**
1. Gather all chapter audio files
2. Create full audiobook:
   - Concatenate all chapters in order
   - Add intro/outro (optional)
   - Embed metadata (title, author, chapters)
3. Generate deliverables:
   - Full audiobook MP3
   - Individual chapter files (already have)
   - Scripts ZIP archive
   - Metadata JSON
   - Chapter markers file
4. Upload all to S3
5. Create `Deliverable` records in database
6. Mark job as completed

**Estimated effort:** 2 days

---

#### 6. Storage Service (AWS S3)

**File:** `backend/services/storage.py`
**Status:** 0% complete (TODO)
**Dependencies:** `boto3`

**What needs to be done:**
1. Initialize S3 client with credentials from settings
2. Implement upload:
   - Generate unique S3 key (e.g., `jobs/{job_id}/audio/{chapter_number}.mp3`)
   - Upload file with proper content type
   - Set ACL to public-read for player access
3. Implement download (for admin/debugging)
4. Implement signed URL generation (for private files)
5. Implement delete (for job cleanup)

**Example structure:**

```python
async def upload_audio_file(
    job_id: str,
    chapter_number: int,
    file_path: str
) -> str:
    """Upload audio file to S3 and return public URL."""
    # TODO: Implement
    pass
```

**Estimated effort:** 1 day

---

#### 7. Payment Service (Stripe)

**File:** `backend/services/payment.py`
**Status:** 0% complete (TODO)
**Dependencies:** `stripe`

**What needs to be done:**
1. Initialize Stripe client
2. Implement payment intent creation:
   - Calculate price based on depth tier
   - Create Stripe PaymentIntent
   - Return client secret for frontend
3. Implement webhook handler:
   - Verify webhook signature
   - Handle `payment_intent.succeeded` event
   - Update job payment status
   - Trigger workflow if payment successful
4. Implement refund (for failed jobs)

**Pricing:**
- Survey: $19 = 1900 cents
- Standard: $49 = 4900 cents
- Comprehensive: $99 = 9900 cents

**Estimated effort:** 1-2 days

---

### Medium-Priority Tasks

#### 8. Authentication System

**Files:** `backend/utils/auth.py`, `backend/api/routes/auth.py`
**Status:** Scaffold exists, logic TODO

**What needs to be done:**
1. Implement JWT token generation/validation
2. Implement password hashing (bcrypt)
3. Create `get_current_user` dependency for protected routes
4. Implement refresh token flow
5. Add rate limiting for login attempts

**Estimated effort:** 1-2 days

---

#### 9. Database Migrations (Alembic)

**File:** `backend/db/migrations/`
**Status:** Folder exists, not configured

**What needs to be done:**
1. Initialize Alembic: `alembic init backend/db/migrations`
2. Configure `alembic.ini` with database URL
3. Update `env.py` to import models
4. Generate initial migration: `alembic revision --autogenerate -m "Initial schema"`
5. Apply migration: `alembic upgrade head`
6. Document migration workflow in README

**Estimated effort:** 0.5 days

---

#### 10. WebSocket Real-Time Updates

**Files:** `backend/api/events.py`, frontend dashboard
**Status:** Event definitions exist, no WebSocket server

**What needs to be done:**
1. Add WebSocket endpoint to FastAPI
2. Implement connection manager for active connections
3. Emit events when job status changes:
   - `job.status_changed`
   - `job.progress_updated`
   - `chapter.completed`
4. Frontend: Connect to WebSocket in dashboard
5. Frontend: Update UI when events received

**Estimated effort:** 1-2 days

---

#### 11. Input Validation

**File:** `backend/utils/validators.py`
**Status:** TODO

**What needs to be done:**
1. Validate GitHub URLs (format, accessibility)
2. Validate Git refs (branches, tags exist)
3. Repository size limits (prevent massive repos)
4. Rate limiting per user
5. Credit/quota checks

**Estimated effort:** 1 day

---

### Low-Priority (Post-MVP)

- Docling integration (IBM parser for richer AST)
- Code visualization in player
- Transcript search
- Offline downloads
- Referral/affiliate system
- Advanced analytics dashboard
- Email notifications

---

## Testing Strategy

### Current Status

**Frontend:** No tests yet (planned: Vitest + React Testing Library)
**Backend:** Pytest installed, minimal tests

### Test Structure

```
backend/tests/
├── test_models.py       # Database model tests
├── test_routes.py       # API endpoint tests
├── test_services.py     # Service logic tests
├── test_agents.py       # Agent behavior tests
└── test_workflows.py    # End-to-end workflow tests
```

### Writing Backend Tests

**Example: Testing a route**

```python
# File: backend/tests/test_routes.py

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.session import get_db
from backend.models.user import User

client = TestClient(app)

@pytest.fixture
def test_db():
    """Create test database session."""
    # TODO: Set up test database
    pass

@pytest.fixture
def test_user(test_db):
    """Create test user."""
    user = User(
        email="test@example.com",
        name="Test User",
        subscription_tier="free"
    )
    test_db.add(user)
    test_db.commit()
    return user

def test_create_job(test_user):
    """Test job creation endpoint."""
    response = client.post(
        "/api/v1/jobs",
        json={
            "repo_url": "https://github.com/user/repo",
            "depth_tier": "standard",
            "git_ref": "main"
        },
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["repo_url"] == "https://github.com/user/repo"
    assert data["status"] == "pending"
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=backend --cov-report=html

# Frontend tests (when implemented)
npm run test
```

---

## Deployment & CI/CD

### Current CI/CD Pipeline

**File:** `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm install --legacy-peer-deps
      - run: npm run build

  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install pytest pytest-asyncio
      - run: pytest
```

**What's missing:** Deployment step (no automatic deploy to production)

### Recommended Deployment Setup

#### Option 1: Railway (Easiest)

1. Frontend and backend in same repo (monorepo)
2. Create two Railway services:
   - Frontend: Node.js service, runs `npm run build && npm run preview`
   - Backend: Python service, runs `uvicorn backend.main:app`
3. Add PostgreSQL database service
4. Set environment variables in Railway dashboard
5. Connect GitHub repo for automatic deploys

#### Option 2: Render

Similar to Railway, good free tier for testing

#### Option 3: AWS (Production-Ready)

- Frontend: S3 + CloudFront
- Backend: ECS Fargate or App Runner
- Database: RDS PostgreSQL
- Storage: S3 for audio files

### Environment Variables in Production

**Frontend (.env.production):**
```bash
VITE_API_BASE_URL=https://api.codebaseaudiobook.com/api/v1
```

**Backend (set in deployment platform):**
```bash
DATABASE_URL=postgresql://user:password@host:5432/audiobook
ANTHROPIC_API_KEY=sk-ant-...
AWS_ACCESS_KEY_ID=...
STRIPE_SECRET_KEY=sk_live_...
# ... all others from backend/.env.example
```

---

## Common Tasks & Patterns

### Adding a New API Endpoint

1. **Define Pydantic schemas** (`backend/api/schemas/my_feature.py`):
   ```python
   class MyFeatureRequest(BaseModel):
       field1: str
       field2: int

   class MyFeatureResponse(BaseModel):
       result: str
   ```

2. **Create route handler** (`backend/api/routes/my_feature.py`):
   ```python
   from fastapi import APIRouter, Depends
   from backend.api.schemas.my_feature import MyFeatureRequest, MyFeatureResponse

   router = APIRouter(prefix="/my-feature", tags=["my-feature"])

   @router.post("", response_model=MyFeatureResponse)
   async def create_feature(data: MyFeatureRequest):
       # Implementation
       return MyFeatureResponse(result="success")
   ```

3. **Register router** (`backend/main.py`):
   ```python
   from backend.api.routes import my_feature
   app.include_router(my_feature.router, prefix="/api/v1")
   ```

4. **Add to API client** (`src/lib/api.ts`):
   ```typescript
   async createFeature(data: MyFeatureRequest): Promise<MyFeatureResponse> {
     return this.request('/my-feature', { method: 'POST', body: data });
   }
   ```

5. **Use in frontend**:
   ```typescript
   const result = await apiClient.createFeature({ field1: "value", field2: 123 });
   ```

### Adding a New Frontend Page

1. **Create page component** (`src/pages/MyPage.tsx`):
   ```typescript
   import { useQuery } from '@tanstack/react-query';
   import { apiClient } from '@/lib/api';

   export default function MyPage() {
     const { data, isLoading } = useQuery({
       queryKey: ['my-data'],
       queryFn: () => apiClient.getMyData()
     });

     if (isLoading) return <div>Loading...</div>;

     return <div>{/* Page content */}</div>;
   }
   ```

2. **Add route** (`src/App.tsx`):
   ```typescript
   import MyPage from '@/pages/MyPage';

   <Route path="/my-page" element={<MyPage />} />
   ```

3. **Add navigation link** (in appropriate component):
   ```typescript
   <Link to="/my-page">My Page</Link>
   ```

### Implementing an Agent Tool

1. **Create tool function** (`backend/tools/my_tools.py`):
   ```python
   def my_tool_function(param1: str, param2: int) -> dict:
       """
       Tool description for the agent to understand when to use it.

       Args:
           param1: Description
           param2: Description

       Returns:
           Dictionary with results
       """
       # Implementation
       return {"result": "data"}
   ```

2. **Wrap as FunctionTool**:
   ```python
   from agent_framework.tools import FunctionTool

   my_tool = FunctionTool(
       name="my_tool",
       description="Clear description for agent",
       func=my_tool_function
   )
   ```

3. **Add to agent** (`backend/agents/my_agent.py`):
   ```python
   from backend.tools.my_tools import my_tool

   agent = Agent(
       name="MyAgent",
       instructions="...",
       tools=[my_tool],
       chat_client=client
   )
   ```

### Running the Full Stack Locally

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your API keys
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm install --legacy-peer-deps
cp .env.example .env  # Edit if needed
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

---

## Troubleshooting

### Common Issues

#### "Module not found" errors (Frontend)

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

#### "Cannot import name..." errors (Backend)

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version (must be 3.11+)
python --version
```

#### Database connection errors

```bash
# Check DATABASE_URL in backend/.env
# For development, SQLite should work:
DATABASE_URL=sqlite:///./audiobook.db

# For PostgreSQL:
DATABASE_URL=postgresql://user:password@localhost:5432/audiobook
```

#### CORS errors in browser

```bash
# Backend CORS is configured for localhost:5173 by default
# If using different port, update backend/main.py:
origins = [
    "http://localhost:5173",  # Add your port here
]
```

#### Agent Framework import errors

```bash
# Agent Framework is in beta, ensure correct version:
pip install agent-framework==1.0.0b251016

# Check if it's importable:
python -c "from agent_framework import Agent; print('OK')"
```

### Getting Help

1. **Search TODO comments** for implementation notes: `grep -r "TODO:" backend/`
2. **Check reference samples** in `samples/` folder
3. **Review plan documents** in `plans/` folder
4. **Read Microsoft Agent Framework docs**: https://learn.microsoft.com/en-us/agent-framework/
5. **Check existing issues** on GitHub

---

## Future Roadmap

### Phase 1: MVP (Current Focus)

- ✅ Frontend UI complete
- ❌ Backend services implementation
- ❌ Basic workflow orchestration
- ❌ Payment integration
- ❌ Audio generation pipeline

### Phase 2: Polish & Launch

- Docling parser integration (richer code analysis)
- WebSocket real-time updates
- Email notifications
- Landing page and marketing site
- Product Hunt launch

### Phase 3: Features & Scale

- Code visualization in player
- Transcript search
- Offline downloads
- Team collaboration features
- API access for enterprises
- Multiple voice options

### Phase 4: Advanced

- PR audiobooks (diff mode)
- Custom voice training
- Multi-language support
- Self-hosted option for enterprises

---

## Key Files Reference

### Must-Read Documentation

| File | Purpose | Status |
|------|---------|--------|
| `README.md` | User-facing setup guide | ✅ Accurate |
| `Plan.md` | Investor spec, architecture vision | 📋 Aspirational |
| `BACKEND_IMPLEMENTATION_PLAN.md` | Detailed technical architecture | 📋 Planned, not all done |
| `CLAUDE.MD` (this file) | AI assistant guide | ✅ Reality check |

### Critical Implementation Files

| File | Purpose | Status |
|------|---------|--------|
| `backend/services/repository_analyzer.py` | Code parsing | ❌ TODO |
| `backend/services/outline_generator.py` | Chapter planning | ❌ TODO |
| `backend/services/script_generator.py` | Narration writing | ❌ TODO |
| `backend/services/audio_synthesizer.py` | TTS | ❌ TODO |
| `backend/services/post_processor.py` | Audio merging | ❌ TODO |
| `backend/services/storage.py` | S3 operations | ❌ TODO |
| `backend/services/payment.py` | Stripe | ❌ TODO |
| `backend/workflows/audiobook_workflow.py` | Orchestration | ~ Partial |

### Frontend Entry Points

| File | Purpose |
|------|---------|
| `src/App.tsx` | Router configuration |
| `src/lib/types.ts` | Type definitions (single source of truth) |
| `src/lib/api.ts` | API client |
| `src/contexts/AuthContext.tsx` | Authentication state |

### Configuration

| File | Purpose |
|------|---------|
| `backend/config.py` | Backend settings (env vars) |
| `.env.example` | Frontend env template |
| `backend/.env.example` | Backend env template |
| `vite.config.ts` | Frontend build config |
| `tailwind.config.ts` | Styling theme |

---

## Final Notes for AI Assistants

### When You Start Working

1. **Always check current implementation status** before assuming something exists
2. **Search for TODO comments** in the file you're working on
3. **Follow existing patterns** - don't introduce new architectural approaches
4. **Test your changes** - at minimum, verify imports and basic functionality
5. **Update this file** if you implement a major component

### What to Prioritize

**Highest value:**
1. Implement repository analyzer (unlocks everything else)
2. Implement outline generator (enables user flow)
3. Implement script generator (core value)
4. Implement audio synthesizer (delivers the product)

**Medium value:**
1. Database migrations (stability)
2. Authentication (security)
3. Payment processing (monetization)

**Lower priority:**
1. WebSocket updates (nice UX)
2. Advanced features (post-MVP)

### Architecture Principles

1. **Type safety everywhere** - Use TypeScript interfaces and Pydantic schemas
2. **Services own business logic** - Routes are thin, services are thick
3. **Agents are specialized** - Each agent has one clear responsibility
4. **Checkpoint frequently** - Enable resume after failures
5. **Log everything important** - Debugging is critical for AI workflows
6. **Track costs** - LLM and TTS usage must be monitored

### Code Quality Standards

- ✅ Type hints on all Python functions
- ✅ TypeScript strict mode, no `any` types
- ✅ Meaningful variable names
- ✅ Docstrings on public functions
- ✅ Error handling with specific exceptions
- ✅ Logging at INFO level for key operations
- ✅ Tests for critical paths (when adding new code)

---

**Last Updated:** October 25, 2025
**Maintainer:** Project Team
**Questions?** Open an issue on GitHub

---

*This guide is maintained to help AI assistants quickly understand the codebase and contribute effectively. Update it as the project evolves.*
