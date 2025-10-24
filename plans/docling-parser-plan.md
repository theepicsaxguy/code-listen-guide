# Docling Parser Integration Plan

## Objective
Adopt IBM's Docling toolkit as the primary parser for repository analysis so that the backend produces structured code maps with
richer syntax information than the current placeholder implementation.

## Assumptions & Open Questions
- "Docling" refers to IBM's Docling parser toolkit; confirm the exact package name, licensing terms, and Python bindings.
- Repository analysis continues to run inside the backend service under `backend/services/repository_analyzer.py`.
- Output schema should remain compatible with downstream agents unless revisions are explicitly scheduled.
- Need clarity on supported languages we must prioritize for the first release (Python, TypeScript/JavaScript, etc.).

## Milestones
1. **Discovery & Prototype**
   - Evaluate Docling documentation and install instructions; confirm compatibility with the project's Python runtime.
   - Spike a small script that parses a representative file set (Python, TypeScript, Markdown) to validate performance and API ergonomics.
   - Document gaps (unsupported languages, missing features) and mitigation strategies.

2. **Dependency & Environment Setup**
   - Add the Docling package to `backend/requirements.txt` (and any system-level prerequisites).
   - Extend local and CI setup scripts to install Docling; capture version pinning strategy.
   - Update developer documentation with setup notes and troubleshooting guidance.

3. **Parser Abstraction Update**
   - Refactor `backend/tools/code_parser_tools.py` to expose a richer parsing interface (e.g., `build_code_map` returning structured nodes, symbol tables, comments).
   - Encapsulate Docling-specific logic behind a thin adapter so we can fall back to alternative parsers if needed.
   - Implement graceful degradation for files Docling cannot parse (record diagnostics instead of failing the entire run).

4. **Repository Analyzer Integration**
   - Modify `backend/services/repository_analyzer.py` to consume the enhanced parsing output, updating any downstream data transformations.
   - Ensure agents using `build_code_map` (e.g., `backend/agents/analyzer_agent.py`) can leverage the new structure without major rewrites.
   - Introduce unit tests covering Docling-driven parsing across multiple file types and error scenarios.

5. **Performance & Quality Validation**
   - Benchmark Docling parsing against the current implementation on mid-sized repositories; profile CPU/memory usage.
   - Establish acceptance criteria (parse coverage %, max runtime) and iterate until we meet them.
   - Run end-to-end agent workflows to confirm narratives benefit from richer parsing data.

6. **Documentation & Rollout**
   - Update backend README and any relevant user-facing docs explaining Docling integration, limitations, and configuration flags.
   - Prepare migration notes detailing required actions for deploy environments.
   - Schedule a feature flag or phased rollout if Docling significantly changes runtime characteristics.

## Risks & Mitigations
- **Library Stability:** Mitigate by pinning Docling versions and monitoring release notes.
- **Language Coverage Gaps:** Keep fallback parsers for unsupported languages and track demand signals to prioritize future work.
- **Performance Regressions:** Introduce profiling hooks and CI checks to guard against timeouts.
- **Operational Complexity:** Automate Docling installation steps and bake health checks into our deployment workflows.

## Success Criteria
- Docling parses at least 95% of targeted files without fatal errors.
- Repository analyzer exposes AST-level data that downstream agents can consume for richer narration.
- Tests and documentation accurately reflect the new parsing pipeline.
