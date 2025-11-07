# Migration Guide: chonkie Parser Integration & Cookie Auth

## Release: v0.2.3
**Date:** January 8, 2026

This release fixes the most common startup traps when provisioning a fresh database.

### 1. Alembic upgrades happen before metadata scaffolding

**What changed:**
- `backend/db/session.py` now runs Alembic migrations before touching `Base.metadata`
  so branch-aware upgrades create the schema instead of the ORM doing it first.
- Alembic is instructed to upgrade all heads, matching the branched history in
  `backend/db/migrations/versions/`.

**Migration required:** None. The application automatically applies all branches
in order during startup.

**Benefits:**
- Prevents `relation already exists` crashes on brand-new databases.
- Keeps divergent migration branches in sync without manual merge targeting.

### 2. Postgres-friendly defaults for local tooling

**What changed:**
- `backend/alembic.ini` defaults to a Postgres connection string so CLI commands
  use the same dialect as runtime migrations.
- `backend/config.py` looks for project-level `.env.development` and `.env` files
  before falling back to `backend/.env`, mirroring how developers usually store
  credentials.

**Migration required:** Update local environment files if they relied on the old
SQLite default.

**Benefits:**
- Alembic CLI invocations succeed with Postgres-specific types.
- Fresh checkouts no longer need duplicate env files to satisfy the settings loader.

## Release: v0.2.2
**Date:** November 6, 2025

This release makes sure the application upgrades the database schema before serving requests.

### 1. Automatic Alembic Upgrades on Startup

**What changed:**
- `backend/db/session.py` now loads `alembic.ini`, overrides the database URL with runtime settings, and calls `alembic upgrade head` during startup.
- The legacy `is_admin` column safeguard runs after the Alembic upgrade to support databases created before migrations existed.

**Migration required:**
- No manual action required for fresh deployments; upgrades happen automatically when the app imports the database session module.
- Existing deployments should confirm that `backend/alembic.ini` is present wherever the app runs so the automatic upgrade can succeed.

**Benefits:**
- Keeps the runtime schema in sync with SQLAlchemy models without a separate deployment step.
- Prevents missing column errors when new migrations introduce fields such as `tools_registry.stable_slug`.

## Release: v0.2.1
**Date:** November 2, 2025

This release hardens the workflow registry so runtime policy checks can depend on
database state instead of in-memory assumptions.

### 1. Tool Registry Versioning & Seeds

**What changed:**
- Added `schema_version` and `updated_at` columns to `tools_registry`
- Enforced a unique constraint on each (`module_path`, `function_name`) pair
- Seeded the registry with the eight core `_ai_*` tool bindings used by the
  analyzer, script, audio, and post-process agents

**Migration required:**
- Run the new Alembic migration to add the metadata columns and populate the
  seeds:
  ```bash
  alembic upgrade head
  ```
- Existing deployments should confirm there are no duplicate module/function
  pairs before applying the migration; the upgrade will fail fast if duplicates
  exist

**Benefits:**
- Provides deterministic version tracking for plugin schemas
- Ensures runtime lookups can disambiguate tools that share names but live in
  different modules
- Preloads the registry with the default audiobook toolchain so new
  environments are ready without running the seed script manually

### 2. Agent Access Control Metadata

**What changed:**
- Added `access_policies` and `quota_limits` JSONB columns to
  `agents_registry`

**Migration required:** None beyond applying the Alembic upgrade.

**Benefits:**
- Stores allow-list and quota configuration alongside each agent for policy
  enforcement during workflow execution

---

## Release: v0.2.0
**Date:** October 29, 2025

This release introduces major improvements to parsing capabilities and authentication security.

## Summary of Changes

### 1. Parser Stack: Docling → chonkie

**What changed:**
- Complete replacement of Docling parser with IBM's chonkie toolkit
- Advanced parsing, cleaning, and tagging pipeline for rich semantic metadata
- New `/api/v1/parse/repository` endpoint for on-demand repository analysis
- Enhanced framework detection, pattern recognition, and dependency graph generation

**Migration required:**
- **Dependencies:** Update `backend/requirements.base.txt` - chonkie replaces docling-core
- **Environment:** No new environment variables required
- **Database:** No schema changes
- **API:** New endpoint available but existing job workflow unchanged

**Breaking changes:** None. Existing job submissions continue to work.

**Benefits:**
- Richer code structure extraction with semantic tags
- Better framework and pattern detection
- Cleaner content normalization
- Improved entry point identification

**Documentation:** See [`decisions/chonkie_PIPELINE.md`](decisions/chonkie_PIPELINE.md) for complete pipeline details.

---

### 2. Authentication: Cookie-Based JWT Storage

**What changed:**
- JWT tokens now stored in HttpOnly cookies instead of localStorage
- Both cookie and Authorization header authentication supported
- Enhanced security against XSS attacks
- CORS configured with `credentials: 'include'` for cookie transmission

**Migration required:**
- **Frontend:** All API calls now use `credentials: 'include'` (already updated)
- **Backend:** CORS already configured with `allow_credentials=True`
- **Cookies:** Two cookies set on login:
  - `access_token` (HttpOnly, Secure in production, 7d expiry)
  - `refresh_token` (HttpOnly, Secure in production, 30d expiry)

**Breaking changes:** 
- None for API consumers using bearer tokens
- Frontend users automatically migrated on next login

**Security improvements:**
- Cookies set with `HttpOnly=True` flag (not accessible to JavaScript)
- `Secure=True` in production (HTTPS only)
- `SameSite=Lax` protection against CSRF
- Automatic token refresh using refresh_token cookie

**API compatibility:**
- Authorization header still supported: `Authorization: Bearer <token>`
- Cookie auth automatically used when cookies present
- Swagger UI `/docs` works with both methods

---

### 3. New Admin Page: chonkie Test Interface

**What changed:**
- New admin page at `/admin/chonkie-test` for testing parse pipeline
- Interactive configuration of chonkie features
- Real-time parsing results with detailed summaries
- Visual display of languages, frameworks, patterns, and entry points

**Migration required:** None (new feature)

**Access:** Admin users only (admin role required)

---

## Upgrade Steps

### For Developers

1. **Update dependencies:**
   ```bash
   cd backend
   pip install -U -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   # Backend
   uvicorn backend.main:app --reload
   
   # Frontend (separate terminal)
   npm install --legacy-peer-deps
   npm run dev
   ```

3. **Test cookie auth:**
   - Login via `/auth`
   - Check browser DevTools → Application → Cookies
   - Verify `access_token` and `refresh_token` cookies present
   - Both should have HttpOnly flag

4. **Test parse endpoint:**
   - Visit `/admin/chonkie-test`
   - Enter a small public repo URL (e.g., `https://github.com/microsoft/agent-framework/`)
   - Click "Parse Repository"
   - Review summary statistics and detected languages/frameworks

### For Production Deployments

1. **Environment variables:**
   ```bash
   # No new required variables
   # Existing variables still needed:
   DATABASE_URL=postgresql://...
   ANTHROPIC_API_KEY=sk-ant-...
   OPENAI_API_KEY=sk-...
   JWT_SECRET=<secure-random-value>
   ```

2. **CORS configuration:**
   - Already configured with `allow_credentials=True`
   - Ensure `FRONTEND_URL` env var points to production domain
   - HTTPS required in production for secure cookies

3. **Docker deployment:**
   ```bash
   # Single container
   docker build -t codebase-audiobook .
   docker run -p 8000:8000 --env-file backend/.env codebase-audiobook
   
   # Docker Compose
   docker compose up --build
   ```

4. **Verify deployment:**
   - Check `/docs` loads (Swagger UI)
   - Test login flow sets cookies
   - Verify `/api/v1/parse/repository` endpoint available (requires auth)
   - Check security headers in response (CSP, HSTS, etc.)

---

## API Changes

### New Endpoints

**POST /api/v1/parse/repository**
- Requires authentication
- Parses GitHub repository using chonkie pipeline
- Returns structured analysis with file content, metadata, and summaries
- Timeout: 180 seconds
- Request body:
  ```json
  {
    "repo_url": "https://github.com/user/repo",
    "git_ref": "main",
    "max_file_size_kb": 500,
    "enable_code_enrichment": true,
    "enable_formula_enrichment": false,
    "enable_table_extraction": true,
    "include_patterns": ["*.py", "*.ts"],
    "exclude_patterns": ["*test*.py"]
  }
  ```

### Modified Endpoints

**POST /api/v1/auth/login**
- Now sets `access_token` and `refresh_token` cookies
- Still returns tokens in response body for API compatibility
- Cookie attributes: `HttpOnly=True`, `Secure=True` (production), `SameSite=Lax`

**POST /api/v1/auth/register**
- Now sets `access_token` and `refresh_token` cookies
- Still returns tokens in response body for API compatibility

### Authentication Methods

Both methods supported simultaneously:

1. **Cookie authentication (recommended for browsers):**
   - Automatic after login
   - No code changes needed in fetch calls with `credentials: 'include'`

2. **Bearer token (recommended for API clients):**
   ```bash
   curl -H "Authorization: Bearer <token>" https://api.example.com/api/v1/jobs
   ```

---

## Configuration Changes

### Security Headers

Stricter CSP now allows Swagger UI and fonts:
```
default-src 'none';
script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com;
img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net;
font-src 'self' https://fonts.gstatic.com;
```

### Cookie Settings

Development:
```python
httponly=True
secure=False  # Allow HTTP in dev
samesite="lax"
max_age=86400  # access_token: 24 hours
max_age=604800  # refresh_token: 7 days
```

Production:
```python
httponly=True
secure=True  # HTTPS only
samesite="lax"
```

---

## Testing

### Automated Tests

All test markers renamed:
- `@pytest.mark.docling` → `@pytest.mark.chonkie`
- Test file: `test_docling_service.py` → `test_chonkie_service.py`

Run chonkie tests:
```bash
pytest -m chonkie -v
```

Run all tests:
```bash
pytest -v
```

### Manual Testing

1. **Cookie authentication:**
   ```bash
   # Login and capture cookies
   curl -c cookies.txt -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"password"}'
   
   # Use cookies for authenticated request
   curl -b cookies.txt http://localhost:8000/api/v1/auth/me
   ```

2. **Parse endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/parse/repository \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "repo_url": "https://github.com/microsoft/agent-framework/",
       "git_ref": "main"
     }'
   ```

3. **Frontend integration:**
   - Login at `/auth`
   - Open DevTools → Network
   - Verify API calls include `Cookie` header
   - Check `/admin/chonkie-test` page loads and functions

---

## Rollback Plan

If issues arise, rollback is straightforward:

1. **Parser rollback:**
   - Not needed - chonkie is additive, doesn't affect existing jobs
   - Old jobs use existing workflow

2. **Auth rollback:**
   - Cookie auth is backward compatible
   - API clients using bearer tokens unaffected
   - Remove cookie code in `backend/utils/auth.py` and `backend/api/routes/auth.py` if needed

3. **Emergency:**
   ```bash
   git revert <commit-hash>
   docker compose up --build
   ```

---

## Known Issues

None at time of release.

Report issues: https://github.com/theepicsaxguy/code-listen-guide/issues

---

## References

- chonkie documentation: IBM Research chonkie toolkit
- FastAPI cookie auth: [Medium guide](https://fastapitutorial.medium.com/fastapi-securing-jwt-token-with-httponly-cookie-47e0139b8dde)
- CORS credentials: [MDN docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#credentials)
- CSP policy: [MDN CSP guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)

---

**Questions?** Open a GitHub issue or discussion.
