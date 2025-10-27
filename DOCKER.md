# Docker Setup Guide

This guide explains how to build and run the Codebase Audiobook application using Docker.

## Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose v2+
- At least 4GB of available RAM
- 10GB of free disk space

## Quick Start

### 1. Environment Configuration

The Compose stack includes `backend/.env.docker`, which mirrors the production wiring. It pins the API base path to `/api/v1`, points at the bundled Postgres and Redis services, and sets every required secret so containers fail fast if configuration drifts. Update the file before launching if you need to supply real credentials for Anthropic, Stripe, or AWS. Every container reads the same values—no local overrides or environment-specific exceptions.

### 2. Build and Run

```bash
# Build the images
docker compose build

# Start the services
docker compose up

# Or run in detached mode
docker compose up -d
```

The application will be available at:
- **Web app and API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs

### 3. Stop the Services

```bash
# Stop services (keeping containers)
docker compose stop

# Stop and remove containers
docker compose down

# Stop, remove containers, and clean up volumes
docker compose down -v
```

## Architecture

The Docker setup consists of two main services:

### Backend Service
- **Base Image**: Python 3.14.0-slim (digest `sha256:4ed33101ee7ec299041cc41dd268dae17031184be94384b1ce7936dc4e5dead3`)
- **Build Process**: Multi-stage build with separate build and runtime stages
- **Port**: 8000 (internal only, traffic arrives through the proxy)
- **Healthcheck**: HTTP check on `/health` endpoint
- **User**: Runs as non-root `app` user for security
- **Determinism**: OS packages install from a frozen Debian snapshot with explicit version pins, the Python runtime comes from a digest-locked base image, and the backend installs from a hash-locked `backend/requirements.runtime.txt` using `pip install --require-hashes` so every build reuses the same cached wheels. Each stage also exports `SOURCE_DATE_EPOCH=0` to avoid embedding build timestamps in the layers.

### Frontend Service
- **Base Image**: Node 22.21.0-bookworm-slim (digest `sha256:f9f7f95dcf1f007b007c4dcd44ea8f7773f931b71dc79d57c216e731c87a090b`) for the build stage, Nginx 1.29-alpine (digest `sha256:61e01287e546aac28a3f56839c136b31f590273f3b41187a36f46f6a03bbfe22`) for runtime
- **Build Process**: Multi-stage build with deps, build, and production stages
- **Port**: 8080 (exposed on the host)
- **Reverse Proxy**: Requests to `/api/` are forwarded to the backend service at `http://backend:8000`
- **Healthcheck**: HTTP check on root endpoint
- **User**: Runs as non-root `nginx` user

### Redis Service
- **Base Image**: Redis 7.4-alpine
- **Purpose**: Provides shared state for WebSocket coordination and rate limiting backends that require Redis semantics
- **Port**: Internal only; the proxy and backend share it over the Compose network

## Configuration

### Environment Variables

#### Backend Environment (`backend/.env.docker`)

The committed defaults pin every required value to a deterministic setting:
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://audiobook:audiobook_dev_password@postgres:5432/audiobook
CHECKPOINT_DATABASE_URL=postgresql://audiobook:audiobook_dev_password@postgres:5432/audiobook
API_BASE_URL=http://localhost:8080/api/v1
JWT_SECRET=development-secret
ANTHROPIC_API_KEY=dev-anthropic-key
OPENAI_RESPONSES_MODEL=gpt-4o-mini
STRIPE_SECRET_KEY=sk_test_placeholder
STRIPE_WEBHOOK_SECRET=whsec_placeholder
STRIPE_PUBLISHABLE_KEY=pk_test_placeholder
AWS_ACCESS_KEY_ID=dev-access-key
AWS_SECRET_ACCESS_KEY=dev-secret-key
S3_BUCKET_NAME=codebase-audiobooks
S3_REGION=us-east-1
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_STORAGE_URI=memory://
```

Adjust the file with production-grade secrets before deploying anywhere outside local development. The backend fails during startup if any required value is missing or points at an unsupported datastore.

#### Frontend Build Arguments

The frontend never reaches across origins during Compose runs. `Dockerfile.frontend` bakes a single value—`VITE_API_BASE_PATH=/api/v1`—into the bundle so all browser requests reuse the same origin and port that served the web app. If you need to test against a remote deployment, set `VITE_API_BASE_PATH` (or the legacy `VITE_API_BASE_URL`) to a full URL before building the frontend image.

### Docker Compose Configuration

The `docker-compose.yml` file includes:

- **Local builds**: Images are built from local Dockerfiles, not pulled from registry
- **Healthchecks**: Services include health checks for better orchestration
- **Dependency ordering**: Frontend waits for backend to be healthy
- **Restart policy**: Services restart automatically unless manually stopped
- **Environment files**: Backend loads `backend/.env.docker` by default (override with `BACKEND_ENV_FILE`)
- **Frontend build args**: Compose bakes `VITE_API_BASE_PATH=/api/v1` into the frontend build so every browser request stays on the same origin.

## Development Workflow

### Rebuilding After Code Changes

```bash
# Rebuild specific service
docker compose build backend
docker compose build frontend

# Rebuild without cache (if you have issues)
docker compose build --no-cache backend

# Restart specific service
docker compose restart backend
```

### Viewing Logs

```bash
# View all logs
docker compose logs

# Follow logs in real-time
docker compose logs -f

# View logs for specific service
docker compose logs backend
docker compose logs -f frontend
```

### Running Commands in Containers

```bash
# Execute command in running backend container
docker compose exec backend python -m pytest

# Execute shell in backend container
docker compose exec backend bash

# Execute command in frontend container
docker compose exec frontend sh
```

## Troubleshooting

### Build Failures

**Problem**: Python package installation fails with compilation errors

**Solution**: The Dockerfile includes common build dependencies (cmake, build-essential, git, etc.). If you encounter errors about missing libraries, you may need to add system packages to the `backend-build` stage in `Dockerfile`.

Example error patterns:
- `fatal error: Python.h: No such file or directory` → Already included in python:slim base
- `error: command 'cmake' failed` → Already included
- `libpq-fe.h: No such file or directory` → Already included (libpq-dev)

### Runtime Issues

**Problem**: Backend container starts but exits immediately

**Solution**: Check logs for missing environment variables:
```bash
docker compose logs backend
```

Most common issues:
- Missing required API keys (OPENAI_API_KEY or ANTHROPIC_API_KEY)
- Invalid DATABASE_URL
- Missing secret keys (JWT_SECRET, STRIPE_SECRET_KEY)

**Problem**: Frontend shows "Cannot connect to backend"

**Solution**:
1. Confirm the proxy is healthy: `docker compose ps frontend`
2. Hit the health endpoint through the proxy: `curl http://localhost:8080/api/v1/health`
3. If that works, refresh the browser so it picks up the same-origin `/api/` path baked into the bundle.

**Problem**: Browser keeps asking for an old hashed asset (for example `/assets/index-ABC123.js`) after a deploy

**Solution**: The Nginx layer now marks `index.html` responses as `no-store`, so every navigation grabs the latest bundle manifest. If you fork the Dockerfile, keep that cache policy in place; otherwise stale HTML will point to JavaScript files that no longer exist. Clear the browser cache once to recover clients that hit the issue before this fix shipped.

### Permission Issues

**Problem**: Permission denied errors in containers

**Solution**: The images run as non-root users for security. If you need to debug:
```bash
# Run as root temporarily
docker compose exec -u root backend bash
```

### Network Issues

**Problem**: Services can't communicate

**Solution**: Services use Docker's internal network. The frontend proxies `/api/` to `http://backend:8000`, so containers should never reference `localhost` when talking to each other.

## Production Deployment

### Image Versioning

For production, tag your images with versions:

```bash
docker compose build
docker tag code-listen-guide-backend:latest ghcr.io/yourorg/backend:1.0.0
docker tag code-listen-guide-frontend:latest ghcr.io/yourorg/frontend:1.0.0
docker push ghcr.io/yourorg/backend:1.0.0
docker push ghcr.io/yourorg/frontend:1.0.0
```

### Security Considerations

1. **Never commit `.env` files** - They contain secrets
2. **Use specific image tags** - Avoid `:latest` in production
3. **Scan images for vulnerabilities**: `docker scan code-listen-guide-backend:latest`
4. **Update base images regularly** - Rebuild to get security patches
5. **Use secrets management** - Consider Docker Swarm secrets or Kubernetes secrets
6. **Enable HTTPS** - Add a reverse proxy (Nginx, Traefik) with TLS termination

### Production Environment Variables

In production, set:
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@db-host:5432/audiobook
AWS_ACCESS_KEY_ID=<production-key>
STRIPE_SECRET_KEY=sk_live_xxxxx  # Use live keys
```

## Performance Optimization

### Build Cache

Docker uses layer caching to speed up builds. The Dockerfiles are optimized to:
1. Copy dependency files first (package.json, requirements.txt)
2. Install dependencies (cached if files unchanged)
3. Copy application code last (changes frequently)

### Resource Limits

You can add resource limits to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          memory: 512M
```

### Multi-platform Builds

To build for different architectures:

```bash
# Build for linux/amd64 and linux/arm64
docker buildx build --platform linux/amd64,linux/arm64 -t myimage:latest .
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Repository README](README.md) - General development setup
- [Backend Implementation Plan](BACKEND_IMPLEMENTATION_PLAN.md) - Architecture details

## Support

If you encounter issues not covered here:
1. Check the [main README](README.md) for general setup
2. Review the [CLAUDE.MD](CLAUDE.MD) file for architecture details
3. Open an issue on GitHub with:
   - Your Docker version: `docker --version`
   - Your Docker Compose version: `docker compose version`
   - Relevant logs: `docker compose logs`
   - Steps to reproduce the issue
