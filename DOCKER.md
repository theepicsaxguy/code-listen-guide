# Docker Setup Guide

This guide explains how to build and run the Codebase Audiobook application using Docker.

## Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose v2+
- At least 4GB of available RAM
- 10GB of free disk space

## Quick Start

### 1. Environment Configuration

Before running the application, you need to configure environment variables:

```bash
# Copy the example environment files
cp .env.example .env
cp backend/.env.example backend/.env

# Edit backend/.env with your API keys and configuration
# At minimum, you need to set:
# - DATABASE_URL (or use SQLite for local testing)
# - OPENAI_API_KEY or ANTHROPIC_API_KEY
# - STRIPE_SECRET_KEY (for payment processing)
# - AWS credentials (for audio storage)
```

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
- **Frontend**: http://localhost:8081
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

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
- **Base Image**: Python 3.11.11-slim
- **Build Process**: Multi-stage build with separate build and runtime stages
- **Port**: 8000 (mapped to 8001 on host)
- **Healthcheck**: HTTP check on `/health` endpoint
- **User**: Runs as non-root `app` user for security

### Frontend Service
- **Base Image**: Node 22.12.0 (build), Nginx 1.29-alpine (runtime)
- **Build Process**: Multi-stage build with deps, build, and production stages
- **Port**: 8080 (mapped to 8081 on host)
- **Healthcheck**: HTTP check on root endpoint
- **User**: Runs as non-root `nginx` user

## Configuration

### Environment Variables

#### Backend Environment (`backend/.env`)

Required variables:
```bash
# Database (use SQLite for local development)
DATABASE_URL=sqlite:///./audiobook.db

# LLM Provider (at least one required)
OPENAI_API_KEY=sk-xxxxx
# or
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Storage (required for production)
AWS_ACCESS_KEY_ID=xxxxx
AWS_SECRET_ACCESS_KEY=xxxxx
S3_BUCKET_NAME=codebase-audiobooks
S3_REGION=us-east-1

# Payments (required for production)
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

See `backend/.env.example` for all available options.

#### Frontend Environment (`.env`)

```bash
VITE_API_BASE_URL=http://localhost:8001/api/v1
```

### Docker Compose Configuration

The `docker-compose.yml` file includes:

- **Local builds**: Images are built from local Dockerfiles, not pulled from registry
- **Healthchecks**: Services include health checks for better orchestration
- **Dependency ordering**: Frontend waits for backend to be healthy
- **Restart policy**: Services restart automatically unless manually stopped
- **Environment files**: Backend loads `backend/.env` automatically

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
1. Check that backend is healthy: `docker compose ps`
2. Verify VITE_API_BASE_URL points to correct host
3. For browser access, use: `VITE_API_BASE_URL=http://localhost:8001/api/v1`

### Permission Issues

**Problem**: Permission denied errors in containers

**Solution**: The images run as non-root users for security. If you need to debug:
```bash
# Run as root temporarily
docker compose exec -u root backend bash
```

### Network Issues

**Problem**: Services can't communicate

**Solution**: Services use Docker's internal network. The backend should reference the frontend as `http://frontend:8080`, not `http://localhost:8081`.

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
