# Codebase Audiobook

Turn any GitHub repository into a narrated tour you can listen to on the train, at the gym, or while cooking dinner. Codebase Audiobook coordinates a team of Microsoft Agent Framework workers that read source code, craft a structured story, and ship finished audio chapters straight to your browser.

## Why this project exists

Developers spend most of their time understanding existing code, yet the best references still demand full-screen attention. Our research shows two important truths:

- Millions of people already learn through podcasts, and audio-first content raises comprehension when listeners can focus without staring at a screen.
- Indie go-to-market playbooks consistently recommend launching fast, sharing progress in developer communities, and letting real users steer the roadmap.

Codebase Audiobook answers both points. It gives developers a hands-free way to learn a codebase and it is built for early, community-driven iteration.

## How it works (high level)

1. **Repository intake** – The backend clones the repository, walks the tree, and prepares language-specific parsing tasks.
2. **Docling-powered parsing** – IBM's Docling toolkit parses, cleans, and tags code with semantic metadata, enabling richer narratives than basic AST parsing. The pipeline extracts structure, detects frameworks, identifies entry points, and builds dependency graphs.
3. **Narrative planning** – A Content Architect agent designs a chapter outline, calling on semantic clustering tools to group related files and concepts.
4. **Script generation** – A pool of Script Generation agents writes the narration for each chapter in parallel while a Quality agent vets accuracy before anything ships.
5. **Audio assembly** – The Audio Synthesis Coordinator renders text-to-speech tracks, normalizes audio, and packages metadata for the player UI.
6. **Delivery** – Finished chapters and transcripts are published through the Delivery Management agent to storage and streamed back to the web client.

The workflow is orchestrated by the Microsoft Agent Framework using checkpointing, observability, and Azure integrations to keep long-running jobs reliable.

## Repository tour

```text
code-listen-guide/
├── backend/                # FastAPI service and Microsoft Agent Framework workflows
├── public/                 # Static assets served by Vite
├── src/                    # React frontend that streams job state and plays audio
├── docs/                   # Market analysis and user research
├── plans/                  # Product and engineering plans that shape the roadmap
└── samples/                # Reference implementations we study for agent design
```

### Frontend snapshot
- **Stack:** Vite, React 19, TypeScript, Tailwind, shadcn/ui.
- **Focus:** Display job progress, surface chapter outlines, and host the audiobook player.
- **Key scripts:**
  - `npm install` – install dependencies
  - `npm run dev` – start the Vite dev server at <http://localhost:5173>
  - `npm run build` – compile for production (used in CI)
  - `npm run lint` – run ESLint across the app

### Backend snapshot
The backend directory has its own README with full setup instructions, but the quick version is:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Production bundle

Run `./serve-production.sh` from the repository root when you want the production build in one command. The script compiles the frontend, starts the FastAPI server with multiple workers, and serves the built assets through `vite preview`. Override defaults by exporting `BACKEND_PORT`, `FRONTEND_PORT`, or `UVICORN_WORKERS` before launching.

The FastAPI service exposes REST and WebSocket endpoints for managing jobs, running the audiobook workflow, and streaming status updates. It leans on PostgreSQL for persistence, Stripe for payments, Azure OpenAI for reasoning, and AWS S3 for audio storage.

## Development workflow

1. **Clone the repo** and install frontend dependencies.
2. **Run the backend** (see snapshot above) and point the frontend to the API host via environment variables (coming soon to the frontend `.env` template).
3. **Kick off a job** using the `/api/v1/jobs` endpoints, then watch the UI update through the WebSocket event stream.
4. **Iterate with plans in mind**: the Docling parser integration plan drives current backend work, and the launch plan outlines the content and community experiments that should accompany each release.

### Testing
- Frontend: `npm run lint` keeps TypeScript and hooks tidy.
- Backend: from `backend/`, run the marker-driven suites with `pytest -m <marker>` once the virtual environment is active. The CI runner installs the full `backend/requirements.txt`, so every job mirrors local development.
- Full CI: GitHub Actions builds the frontend with Node.js 22 and runs backend unit, workflow, service, agent, API, model, and integration suites on Python 3.11 and 3.12, publishing coverage to Codecov when configured.
- Scheduled checks: nightly integration runs and an always-on code-quality workflow catch slow or lint-related regressions without blocking day-to-day development.

## Roadmap highlights

- **✓ Docling parser integration:** Implemented! The pipeline now parses, cleans, and tags codebases with semantic metadata. See [`docs/DOCLING_PIPELINE.md`](docs/DOCLING_PIPELINE.md) for details.
- **Community-driven launch:** Publish a transparent landing page, collect early-access signups, and share progress across developer forums, newsletters, and Product Hunt.
- **Accessibility enhancements:** Pair every audio chapter with searchable transcripts and navigation cues so listeners can jump between sections quickly (identified as a gap in launch research).

## Reference material

- `docs/DOCLING_PIPELINE.md` – Complete documentation for the Docling parsing, cleaning, and tagging pipeline.
- `docs/analysis.md` – Market demand study for audio-first developer education.
- `Plan.md` – Investor-facing deep dive into the multi-agent architecture and enterprise positioning.
- `plans/*.md` – Execution blueprints for parser upgrades and go-to-market work.
- `samples/` – External agent framework examples that inspire our own workflow design.

## Contributing

Open an issue before starting large changes so we can cross-check with the roadmap. For new features, update the relevant plan files or add a short proposal in `docs/` so future contributors know the reasoning. Pull requests must pass linting, frontend build, and backend tests before review.

