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
COPY backend/requirements.runtime.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip wheel setuptools && \
    python -m pip wheel --no-deps --wheel-dir=/wheels -r requirements.txt

# =============================================================================
# Backend Build Stage
# =============================================================================
FROM python:${PYTHON_VERSION} AS backend-deps
WORKDIR /app
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

RUN python -m venv /opt/venv && /opt/venv/bin/pip install --upgrade pip
COPY backend/requirements.runtime.txt ./requirements.txt
COPY --from=python-deps /wheels /wheels
RUN --mount=type=cache,target=/root/.cache/pip \
    /opt/venv/bin/pip install --find-links=/wheels -r requirements.txt
COPY backend ./backend

# =============================================================================
# Production Runtime Stage
# =============================================================================
FROM python:${PYTHON_VERSION} AS production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

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
COPY --from=backend-deps --chown=app:app /opt/venv /opt/venv
COPY --from=backend-deps --chown=app:app /app/backend /app/backend
COPY --from=frontend-build --chown=app:app /app/dist /app/backend/frontend_dist

USER app
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
