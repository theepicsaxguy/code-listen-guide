# syntax=docker/dockerfile:1.19

ARG PYTHON_VERSION=3.14.0-slim
ARG NODE_VERSION=22.21.0-bookworm-slim
ARG VITE_API_BASE_PATH=/api/v1

# =============================================================================
# Frontend Build Stage
# =============================================================================
FROM node:${NODE_VERSION} AS frontend-deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --frozen-lockfile

FROM node:${NODE_VERSION} AS frontend-build
WORKDIR /app
COPY --from=frontend-deps /app/node_modules ./node_modules
COPY package*.json ./
COPY index.html vite.config.ts tsconfig.json tsconfig.node.json tsconfig.app.json ./
COPY postcss.config.js tailwind.config.ts eslint.config.js components.json ./
COPY public ./public
COPY src ./src
ENV VITE_API_BASE_PATH=${VITE_API_BASE_PATH}
RUN npm run build

# =============================================================================
# Python Wheels Build Stage
# =============================================================================
FROM python:${PYTHON_VERSION} AS python-deps
WORKDIR /wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libssl-dev \
        libffi-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.runtime.txt ./requirements.runtime.txt

# =============================================================================
# System Dependencies Stage (very rarely changes)
# =============================================================================
FROM python:${PYTHON_VERSION} AS system-deps
ENV PYTHONDONTWRITEBYTECODE=1
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        build-essential \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        git \
        cmake \
        pkg-config \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Backend Dependencies Stage (cached)
# =============================================================================
FROM system-deps AS backend-deps
WORKDIR /app
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --upgrade pip
COPY backend/requirements.runtime.txt backend/requirements.base.txt /wheels/
RUN --mount=type=cache,target=/root/.cache/pip \
    cd /wheels && \
    python -m pip install --upgrade pip wheel setuptools && \
    python -m pip wheel --no-deps --wheel-dir=/wheels -r requirements.runtime.txt

# =============================================================================
# Backend Build Stage (source code - changes frequently)
# =============================================================================
FROM backend-deps AS backend-build
WORKDIR /app
COPY backend ./backend

# =============================================================================
# Production Runtime Stage
# =============================================================================
FROM python:${PYTHON_VERSION} AS production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install minimal runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        libxml2 \
        libxslt1.1 \
        zlib1g \
        git \
        curl \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --system app \
    && useradd --system --gid app --home /app --create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Copy built artifacts
COPY --from=backend-build /opt/venv /opt/venv
COPY --from=backend-build /app/backend /app/backend
COPY --from=frontend-build /app/dist /app/backend/frontend_dist

# Ensure virtual environment ownership
RUN chown -R app:app /opt/venv

USER app
EXPOSE 8000
CMD ["/opt/venv/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
