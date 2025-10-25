# Codebase Audiobook — Contributor Guide for Agents

Welcome! Follow these conventions whenever you touch the repository:

## Code Changes
- Stick to TypeScript, Python, and Tailwind patterns already in place. Match existing file structure instead of introducing new directories unless the change would be messy without it.
- Favor clear, single-purpose functions. If you simplify or refactor something, remove dead code while you are there.
- Keep TypeScript strict-friendly: prefer explicit types on exported helpers and React component props.
- Python modules should follow FastAPI idioms with async endpoints and Pydantic models grouped together.

## Documentation
- Update the relevant docs, plans, or READMEs whenever behavior changes. Use the project’s existing headings and narrative style rather than robotic bullet dumps.

## Testing & Tooling
- Frontend: run `npm run lint` before sending a PR.
- Backend: from `backend/`, run `pytest` for service logic.
- If your change touches both sides, run both suites. Fix formatting or lint issues locally before committing.

## Git & PRs
- Use Conventional Commit messages (`feat:`, `fix:`, `docs:` and friends). Squash stray commits before opening the PR.
- Include a short summary and the relevant test results in your PR description so reviewers can skim quickly.

Thanks for helping keep Codebase Audiobook healthy.
