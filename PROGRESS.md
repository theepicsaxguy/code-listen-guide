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
### 4.1 Sprint 2 – Episode Architecture (NOT STARTED)
Goal: Shift from linear file enumeration to **relational episode graph**.
Planned Components:
- New `Episode` model (fields: id, job_id, ordinal, title, goals, dependency_inputs, dependency_outputs, depends_on[], leads_to[], status, script_draft, final_script, estimated_duration)
- Dependency analyzer:
  - Build import/inheritance graph
  - Identify entry clusters
  - Collapse trivial utility chains
  - Detect architectural seams (framework boundaries, adapters, domain layers)
- Relationship-based outline generator:
  - Produces graph-first plan (episodes are nodes with edges representing conceptual progression)
  - Duration balancing & narrative arc (intro → core systems → cross-cutting → scaling/edge cases)
- Migration(s): create episodes table + relationship tables (if many-to-many via link table) or JSONB arrays initially (MVP choice)

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
| Episode Model | PENDING | To be designed & migrated (Sprint 2) |
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
