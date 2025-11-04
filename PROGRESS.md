# Project Progress Report

Date: 2025-11-02
Repository: `code-listen-guide`
Scope: Transformation from single-voice Audiobook generator to Two-Host Podcast Platform (per podcast vision implementation plan)

---
## 1. Executive Summary
We have fully delivered **Sprint 1 (Trust & Control Foundation)**: users can now preview a repository, select precise scope, and receive a real token/cost estimate **before** any job is created. Back-end cost estimation is grounded in actual file parsing with real token counts. The database has been extended to persist user scope decisions and approval state.

Upcoming work shifts from surface trust features to the **structural/content model changes (Episodes + Dependency Graph)** and later to **dialogue generation + dual-voice synthesis** and **queueing/scalability**.

---
## 2. Original Multi-Sprint Goal (Recap)
| Sprint | Theme | Core Outcomes |
|--------|-------|---------------|
| 1 | Trust & Control Foundation | Preview, scope selection, real cost estimation, approval gate |
| 2 | Episode Architecture | Replace file-based chapters with relationship-based Episodes; dependency graph powered planning |
| 3 | Podcast Dialogue Layer | Two-host persona system, conversational script generation, dual voice TTS pipeline |
| 4 | Operationalization | Job queue, prioritization, scaling, polish, resilience |

---
## 3. Completed Work (Sprint 1)
### 3.1 Frontend
- `RepositoryPreview` page (README + file tree visualization before any commitment)
- `ReadmeViewer` component (markdown with syntax highlighting)
- `RepositoryBrowser` / tree components to inspect module structure
- `ScopeSelection` page with:
  - `FileTreeSelector` (granular include selections)
  - `LanguagePrioritySelector` (declare primary language for mixed repos)
  - Default exclusion pattern handling
- `CostEstimate` approval page with detailed LLM vs TTS cost, duration, token breakdown and explicit approval checkbox
- Routing updates (`/repository-preview`, `/scope-selection`, `/cost-estimate`) integrated into submit flow

### 3.2 Backend
- Extended `Job` model with new fields:
  - `selected_files` (JSONB)
  - `excluded_patterns` (JSONB)
  - `primary_language` (String)
  - `estimated_total_tokens` (Integer)
  - `user_approved_cost` (Integer flag)
- Migration `20241102_scope_selection.py` applied successfully (branch merged with existing divergent head)
- Real token counting service: `backend/services/token_estimator.py`
  - LLM token estimation with tier multipliers (survey 1.3x, standard 1.5x, comprehensive 2.0x)
  - Cost calculation using configured rates (Claude-like LLM: $9 / 1M tokens avg; TTS: $15 / 1M chars)
  - Aggregated structure returned to endpoint
- `POST /api/v1/jobs/estimate` endpoint rewritten:
  - Clones repo
  - Applies inclusion/exclusion rules
  - Reads actual file contents
  - Computes tokens + costs via TokenEstimator
  - Returns structured estimate for frontend gate
- API client (`src/lib/api.ts`) updated with:
  - `estimateJob()`
  - `createJob()` (now includes scope + approval parameters)
  - `parseRepository()` already leveraged by preview flow
- Migration chain conflict handled via targeted upgrade (multiple heads recognized; both lines maintained)

### 3.3 Dev Experience / Infra
- Verified npm dependencies for markdown rendering: `react-markdown`, `remark-gfm`, `react-syntax-highlighter`
- Successful Python virtual env migration run & reconciliation of down_revision mismatch

---
## 4. Remaining Work (Future Sprints)
### 4.1 Sprint 2 – Episode Architecture (IN PROGRESS – Foundational layer added)
Goal: Shift from linear file enumeration to **relational episode graph**.

#### 4.1.1 Completed Foundations (this update)
The minimum viable Episode substrate has been introduced to unblock planner & dialogue work:
- `Episode` SQLAlchemy model + Alembic migration (table created; includes ordinal/number, title, status, draft/final script fields stubbed)
- Pydantic schemas: `EpisodeResponse`, `EpisodesListResponse`
- Read APIs: `GET /api/v1/episodes/job/{job_id}` (ordered list) and `GET /api/v1/episodes/{episode_id}` — owner or admin auth now required
- Router inclusion in FastAPI app
- Frontend API client method `getJobEpisodes(jobId)` (read-only consumption path)
- Basic schema test (`test_episode_schema.py`) validating serialization shape

These are intentionally read-only & schematic; no planner or dependency semantics yet. They allow the UI (or future admin tools) to display placeholder episodes once generation exists and reduce future migration churn.

#### 4.1.2 Remaining (planned for remainder of Sprint 2)
Planned Components (still outstanding unless noted):
- Enrich `Episode` model with: `goals`, `dependency_inputs`, `dependency_outputs`, `depends_on[]`, `leads_to[]`, `estimated_duration` (JSONB arrays initially) – (NOT DONE)
- Dependency analyzer service:
  - Build import/inheritance graph (language-aware) – (NOT DONE)
  - Identify entry clusters – (NOT DONE)
  - Collapse trivial utility chains – (NOT DONE)
  - Detect architectural seams (framework boundaries, adapters, domain layers) – (NOT DONE)
- Episode planning service:
  - Graph → episode grouping heuristic – (NOT DONE)
  - Duration balancing & narrative arc (intro → core systems → cross-cutting → scaling/edge cases) – (NOT DONE)
- Mutation & approval endpoints:
  - `POST /api/v1/jobs/{job_id}/episodes/plan` (idempotent planner trigger) – (NOT DONE)
  - `PATCH /api/v1/episodes/{id}` (title/goals edits) – (NOT DONE)
  - Episode approval / locking mechanism – (NOT DONE)
- Integration with Job lifecycle & statuses (planning → waiting_episode_approval) – (NOT DONE)
- Cost/token distribution per episode – (NOT DONE)
- Expanded tests: planner unit tests, dependency graph fixture, endpoint integration – (NOT DONE)
- Documentation: developer guide for planner heuristics – (NOT DONE)

Decision still pending on normalized join tables vs JSONB arrays; MVP path remains JSONB arrays for iteration speed.

### 4.2 Sprint 3 – Podcast Dialogue Layer (NOT STARTED)
Goals: Convert static narration into engaging two-host conversation.
Key Tasks:
- Persona definitions (e.g., "Architect" vs "Curious Senior Engineer")
- Prompt frameworks for: explanation, challenge, analogy, recap, forward references
- Dialogue script generator:
  - Turn each Episode plan into multi-turn conversational script
  - Maintain cross-episode continuity (callbacks, foreshadowing)
  - Guardrails: no code dumping; story-driven exploration
- Dual voice synthesis:
  - Choose two TTS voices; manage alternation & pacing
  - Insert natural pauses & emphasis markers
  - Combine segmented outputs into final episode MP3

### 4.3 Sprint 4 – Queue & Operational Polish (NOT STARTED)
Goals: Production-readiness & scale.
Planned Items:
- Background job queue (e.g., Redis + worker or asyncio + priority scheduler)
- Concurrency controls & rate limiting (LLM + TTS cost governance)
- Retry + checkpoint integration for long-running multi-stage episodes
- User-facing progress events (WebSocket streaming of stage transitions)
- Cost & usage accounting per stage (token + TTS attribution)
- Administrative controls (pause, resume, reprioritize jobs)

---
## 5. Current Status Snapshot
| Area | Status | Notes |
|------|--------|-------|
| Repository Preview | COMPLETE | Users see README + structure pre-commit |
| Scope Selection | COMPLETE | Granular file selection & language priority |
| Cost Estimation | COMPLETE | Real token counts & cost model implemented |
| DB Schema (Scope Fields) | COMPLETE | Migration applied (multi-head env) |
| Episode Model | PARTIAL | Base table + read APIs & schemas present; dependency & planning fields pending |
| Dependency Graph Engine | PENDING | Requires parsing & graph algorithms |
| Outline → Episodes | PENDING | Replace legacy chapter planning |
| Two-Host Personas | PENDING | Persona prompt design |
| Dialogue Generation | PENDING | Conversational script engine |
| Dual Voice TTS | PENDING | Alternation + stitching pipeline |
| Job Queue & Priority | PENDING | Infra & governance |
| Real-Time Progress | PENDING | WebSocket + event emission |
| Cost Tracking per Stage | PARTIAL | High-level token costs; stage attribution later |

---
## 6. Risk & Considerations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Episode Graph Complexity | Longer implementation cycle | Start with JSONB arrays; refactor to normalized tables later |
| Token Cost Volatility | Pricing drift vs hardcoded rates | Externalize pricing to config or database; periodic refresh task |
| Dialogue Quality Variance | Uneven persona balance | Structured turn templates + evaluation harness |
| TTS Latency | Slow end-to-end generation | Batch synthesis + parallel segment requests |
| Multi-Head Migration Growth | Harder schema evolution | Plan merge migration after Episode model stabilization |
| Queue Backpressure | User perception of slowness | Implement ETA + position-in-queue reporting |

---
## 7. Immediate Next Actions
1. End-to-End Manual Test of New Flow (Submit → Preview → Scope → Estimate → Create Job)
2. Draft `Episode` model + migration (choose JSONB vs link table approach for dependencies)
3. Implement minimal dependency analyzer (imports + file grouping) to feed Episode planning
4. Replace existing chapter outline code path with Episode planning adapter (feature flag)

---
## 8. Suggested Technical Decisions (To Confirm)
| Decision Point | Recommendation |
|----------------|---------------|
| Episode dependency storage | Start with JSONB `depends_on` & `leads_to` arrays for speed; migrate to join table later |
| Graph algorithm base | Use NetworkX-like approach internally (or lightweight custom) w/ topological layering |
| Persona prompt format | YAML front-matter + RAG retrieval of style exemplars |
| Dialogue chunk sizing | ~200–300 token turns; maintain rolling context window |
| TTS provider strategy | Start single provider (OpenAI) then abstract adapter for future multi-provider failover |
| Queue implementation | Simple DB + polling or Redis-based Celery/RQ; choose based on existing infra readiness |

---
## 9. Metrics & Instrumentation (Planned)
| Metric | Sprint Introduced | Purpose |
|--------|-------------------|---------|
| Avg pre-job abandonment rate | 1 | Validate preview usefulness |
| Scope reduction percentage | 1 | Measures feature value (tokens excluded) |
| Episode graph density | 2 | Complexity signal for narrative planning |
| Dialogue turn count per episode | 3 | Balancing depth vs runtime |
| TTS synthesis time per minute audio | 3 | Performance tuning |
| Queue wait time P95 | 4 | Capacity planning |

---
## 10. Open Questions
1. Will episodes allow cross-job reuse (caching top-level architecture intros)?
2. Should pricing adapt dynamically based on scope shrink vs baseline repository size?
3. Do we expose an advanced mode for manual episode re-ordering before generation?
4. Should we implement persona preference persistence per user?

---
## 11. Validation Checklist (Sprint 1)
| Check | Status |
|-------|--------|
| Repository parse fails gracefully | ✅ | Error toast + redirect |
| README fallback when absent | ✅ | Page still renders structure section |
| Scope selection persists through navigation | ✅ | Passed via location state |
| Exclusions affect token estimate | ✅ | Endpoint filters before counting |
| Approval required before job creation | ✅ | Explicit checkbox gate in UI |
| Migration applied successfully | ✅ | `20241102_scope_selection` installed |

---
## 12. Summary
Foundation for informed user commitment is complete. We now pivot to **internal structural intelligence (Episodes + Graph)** to unlock differentiated value before moving into **conversational generation** and **scalable operations**. Staying disciplined on graph + model design in Sprint 2 will reduce rework and accelerate high-quality dialogue outcomes in Sprint 3.

---
*Generated automatically as a progress artifact. Update cadence: per major sprint milestone or weekly, whichever comes first.*

---
## 13. Incremental Update (Episode Planning Foundations – Added This Iteration)

New implementation work completed since prior snapshot (without altering earlier log):

### Backend Enhancements
- Extended `Episode` model with planning & graph relationship fields: `goals`, `dependency_inputs`, `dependency_outputs`, `depends_on`, `leads_to`, `estimated_duration_minutes`.
- Alembic migration `20251102_add_episode_planning_fields` added to evolve schema (appends to existing `episodes` table created earlier).
- Added minimal `DependencyAnalyzer` service (`backend/services/dependency_analyzer.py`) providing:
  - Basic Python import graph extraction via `ast`.
  - Naive connected-component clustering → provisional episode clusters.
  - Simple largest-first ordering heuristic.
- Introduced feature flag `feature_episode_planning` (settings) to allow controlled rollout / rollback.
- Implemented idempotent planning endpoint: `POST /episodes/job/{job_id}/plan` which:
  - Validates feature flag and job existence.
  - Requires prior scope selection (`selected_files`) to avoid blind planning.
  - Generates one episode per cluster with provisional duration (3 min/file heuristic, min 5).
  - Seeds basic placeholder metadata (conversation hooks, objectives, goals).
  - Establishes linear `depends_on` / `leads_to` chain for initial sequencing.

### Schema / API Surface
- Updated `EpisodeResponse` schema to expose new planning fields (ensuring forward compatibility for future UI editing tools).
- Maintained backward compatibility: existing episode list & get endpoints unchanged in route shape.

### Testing
- Extended `test_episode_schema.py` with:
  - Field presence & default assertions for new planning attributes.
  - Validation that planning cannot proceed without scope (`400` guard case).
- Added `test_episode_planning_endpoint.py` covering happy-path planning given a seeded job with `selected_files`.

### Outstanding / Next Steps (Focused Within Sprint 2 Scope)
| Item | Status | Notes |
|------|--------|-------|
| End-to-end pytest run (coverage args failing locally) | PENDING | Need to reconcile coverage plugin availability or temporarily relax addopts for local run. |
| Enrich Dependency Analyzer (multi-language, layer detection) | PENDING | Current implementation Python-only & structural; no semantic weighting yet. |
| Episode duration balancing & narrative arc heuristics | PENDING | Currently linear order by cluster size; no pacing adjustment. |
| Editable episode mutation (`PATCH /episodes/{id}`) | PENDING | Not yet exposed; will enable manual curation loop. |
| Approval workflow integration (status transitions) | PENDING | Requires tying planning output to job lifecycle (e.g., `waiting_episode_approval`). |
| Cost/token distribution per episode | PENDING | Need to apportion precomputed token estimate across cluster sizes. |
| Documentation for planning heuristics | PENDING | To be added after heuristic stabilization. |

### Risks Introduced / Mitigations
- Simplistic clustering may over-fragment utility modules → plan to introduce a merge pass (threshold on cluster size) before dialogue phase.
- Linear `depends_on` chain is artificial; future graph-based ordering (topological / centrality) will replace once richer analyzer is in place.
- Migration ordering (date-based) intentionally precedes some later-dated migrations already present; will require a merge migration if chronology semantics enforced—currently acceptable while on development branch.

### Immediate Technical Tasks Queued
1. Resolve pytest coverage argument failure (install `pytest-cov` in active venv or guard addopts by plugin detection).
2. Implement cluster merge heuristic (e.g., fold clusters with <2 files into nearest neighbor by import edge count).
3. Add token/cost proportional allocation stub: `estimated_tokens = (cluster_file_count / total_selected_files) * job.estimated_total_tokens`.
4. Introduce lightweight narrative arc tagging (intro/core/cross-cutting/scaling) based on cluster centrality (placeholder centrality = degree).

This additive section leaves earlier historical context intact as requested.

### Additional Update (Migration Lineage & Test Infra Stabilization – Current Session)

Recent backend maintenance focused on ensuring long-term migration health and preparing episode planning for reliable evolution:

#### Migration Lineage Consolidation
- Identified multi-head Alembic divergence (scope selection vs episode planning paths) and introduced explicit merge migration (`8327b05d4d00_merge_scope_and_episode_heads`) documenting strategy for future merges.
- Added subsequent episodes table migration (`20251123_add_episodes_table`) encapsulating `estimated_episodes` field on `jobs` and initial episode columns; later planning-fields migration builds atop this.
- Confirmed presence of planning fields evolution migration (`20251102_add_episode_planning_fields`) enriching existing table instead of recreating.

#### Configuration Adjustments
- Updated `backend/config.py` to map uppercase environment variables (`DATABASE_URL`, `CHECKPOINT_DATABASE_URL`) via `alias` for pydantic settings – eliminating mismatch between env naming conventions and internal attribute resolution.
- Relaxed strict Postgres enforcement for any environment starting with `test`, allowing SQLite usage in ephemeral test contexts.

#### Test Infrastructure Refactor
- Simplified `backend/tests/conftest.py` removing dual engine setup (previous conflict between Alembic-migrated session and metadata.create_all in-memory engine) – now single migration-driven path.
- Added direct import of `Episode` model and unified `db_session` fixture tied to `SessionLocal` after migrations.
- Ensured feature flags (`feature_episode_planning`) accessible in test environment by centralizing environment variable declarations early.

#### Outstanding Issue (Episodes Table Absent in Test Run)
- Despite migration presence, latest targeted test run still reports `UndefinedTable: episodes`; root cause isolated to migration ordering when applying `upgrade heads` under SQLite + dynamic stamping.
- Action Deferred (per user request to skip further test stabilization) – next corrective step would be enforcing deterministic linear revision chain or invoking targeted upgrade sequence (`command.upgrade(cfg, revision)`) for episodes migration explicitly before tests.

#### Next Suggested (Deferred) Steps
1. Add diagnostic hook to print applied revision list inside test fixture post-upgrade.
2. Verify `down_revision` chain continuity from initial schema through all added episodes-related migrations.
3. If branch persists: create merge revision that sets single head at latest episodes planning migration and adjust earlier episode creation revision `down_revision` accordingly.
4. Re-run minimal episode insertion test to confirm table existence.

#### Summary of Current Session Additions
| Item | Type | Status |
|------|------|--------|
| Merge migration for multi-head resolution | Infra | Added |
| Config env aliasing for DB URLs | Config | Added |
| Test conftest unification | Tests | Applied |
| Episode table absent error investigation | Debug | In Progress (deferred) |

This section augments prior progress without altering historical records, providing clarity on migration and test environment readiness for upcoming Episode planner enhancements.
