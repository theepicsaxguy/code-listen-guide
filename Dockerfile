# syntax=docker/dockerfile:1.19

ARG PYTHON_IMAGE=python:3.14.0-slim@sha256:9813eecff3a08a6ac88aea5b43663c82a931fd9557f6aceaa847f0d8ce738978
ARG NODE_IMAGE=node:24.20.0-bookworm-slim@sha256:ba849c60be29959425b8734d57b8b4b7d56f98edd9504c9af091d5281095a71e
ARG NPM_VERSION=10.9.2
ARG VITE_API_BASE_PATH=/api/v1
ARG DEBIAN_RELEASE=trixie
ARG DEBIAN_SNAPSHOT=20251008T000000Z
ARG SNAPSHOT_BASE_URL=https://snapshot.debian.org/archive

# =============================================================================
# Frontend Build Stage
# =============================================================================
FROM ${NODE_IMAGE} AS frontend-deps
ARG NPM_VERSION
WORKDIR /app
ENV SOURCE_DATE_EPOCH=0
# Pin npm version for reproducibility
RUN npm install -g npm@${NPM_VERSION}
COPY package.json package-lock.json ./
RUN npm ci --frozen-lockfile

FROM ${NODE_IMAGE} AS frontend-build
ARG NPM_VERSION
WORKDIR /app
ENV SOURCE_DATE_EPOCH=0
RUN npm install -g npm@${NPM_VERSION}
COPY --from=frontend-deps /app/node_modules ./node_modules
COPY package*.json ./
COPY index.html vite.config.ts tsconfig.json tsconfig.node.json tsconfig.app.json ./
COPY postcss.config.js tailwind.config.ts eslint.config.js components.json ./
COPY public ./public
COPY src ./src
ENV VITE_API_BASE_PATH=${VITE_API_BASE_PATH}
RUN npm run build

# =============================================================================
# Python Base Stage (snapshot-pinned apt sources)
# =============================================================================
FROM ${PYTHON_IMAGE} AS python-base
ARG DEBIAN_RELEASE
ARG DEBIAN_SNAPSHOT
ARG SNAPSHOT_BASE_URL
ENV SOURCE_DATE_EPOCH=0
RUN set -eux; \
    rm -f /etc/apt/sources.list.d/debian.sources; \
    printf 'deb [check-valid-until=no] %s/debian/%s %s main\n' "${SNAPSHOT_BASE_URL}" "${DEBIAN_SNAPSHOT}" "${DEBIAN_RELEASE}" > /etc/apt/sources.list; \
    printf 'deb [check-valid-until=no] %s/debian-security/%s %s-security main\n' "${SNAPSHOT_BASE_URL}" "${DEBIAN_SNAPSHOT}" "${DEBIAN_RELEASE}" >> /etc/apt/sources.list; \
    printf 'deb [check-valid-until=no] %s/debian/%s %s-updates main\n' "${SNAPSHOT_BASE_URL}" "${DEBIAN_SNAPSHOT}" "${DEBIAN_RELEASE}" >> /etc/apt/sources.list; \
    printf 'Acquire::Check-Valid-Until "false";\n' > /etc/apt/apt.conf.d/90snapshot

# =============================================================================
# Python Wheels Build Stage
# =============================================================================
FROM python-base AS python-deps
ARG DEBIAN_RELEASE
ARG DEBIAN_SNAPSHOT
ARG SNAPSHOT_BASE_URL
WORKDIR /wheels
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    set -eux; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential=12.12 \
        python3-dev=3.13.5-1 \
        libssl-dev=3.5.1-1+deb13u1 \
        libffi-dev=3.4.8-2 \
        libpq-dev=17.6-0+deb13u1; \
    rm -rf /var/lib/apt/lists/*
COPY backend/requirements.runtime.txt ./requirements.runtime.txt

# =============================================================================
# System Dependencies Stage (very rarely changes)
# =============================================================================
# NOTE: Reproducibility strategy:
# 1. Pinned base image (python:3.14.0-slim@sha256:...)
# 2. Debian snapshot from base image build date (20251008T000000Z)
# 3. All Debian packages pinned to snapshot versions
# 4. Python packages pinned (pip, wheel, setuptools)
# This ensures consistent builds and effective Docker layer caching.
FROM python-base AS system-deps
ARG DEBIAN_RELEASE
ARG DEBIAN_SNAPSHOT
ARG SNAPSHOT_BASE_URL
ENV PYTHONDONTWRITEBYTECODE=1
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    set -eux; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ffmpeg=7:7.1.2-0+deb13u1 \
        build-essential=12.12 \
        libxml2-dev=2.12.7+dfsg+really2.9.14-2.1+deb13u1 \
        libxslt1-dev=1.1.35-1.2+deb13u2 \
        zlib1g-dev=1:1.3.dfsg+really1.3.1-1+b1 \
        git=1:2.47.3-0+deb13u1 \
        cmake=3.31.6-2 \
        pkg-config=1.8.1-4 \
        libssl-dev=3.5.1-1+deb13u1 \
        libffi-dev=3.4.8-2 \
        libpq-dev=17.6-0+deb13u1 \
        curl=8.14.1-2; \
    rm -rf /var/lib/apt/lists/*

# =============================================================================
# Backend Dependencies Stage (cached)
# =============================================================================
FROM system-deps AS backend-deps
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# Use clean requirements.txt (11 packages) instead of bloated runtime.txt (3286 lines)
COPY backend/requirements.txt backend/requirements.base.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    /opt/venv/bin/pip install --cache-dir /root/.cache/pip \
        pip==25.3 \
        wheel==0.45.1 \
        setuptools==80.9.0 && \
    /opt/venv/bin/pip install --cache-dir /root/.cache/pip -r requirements.txt

# =============================================================================
# Backend Build Stage (source code - changes frequently)
# =============================================================================
FROM backend-deps AS backend-build
WORKDIR /app
COPY backend ./backend

# =============================================================================
# Production Runtime Stage
# =============================================================================
FROM python-base AS production
ARG DEBIAN_RELEASE
ARG DEBIAN_SNAPSHOT
ARG SNAPSHOT_BASE_URL
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install minimal runtime dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    set -eux; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ffmpeg=7:7.1.2-0+deb13u1 \
        libxml2=2.12.7+dfsg+really2.9.14-2.1+deb13u1 \
        libxslt1.1=1.1.35-1.2+deb13u2 \
        zlib1g=1:1.3.dfsg+really1.3.1-1+b1 \
        git=1:2.47.3-0+deb13u1 \
        curl=8.14.1-2 \
        libpq5=17.6-0+deb13u1; \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --system app \
    && useradd --system --gid app --home /app --create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Copy built artifacts
COPY --from=backend-build /opt/venv /opt/venv
COPY --from=backend-build /app/backend /app/backend
COPY --from=frontend-build /app/dist /app/backend/frontend_dist

USER app
EXPOSE 8000
CMD ["/opt/venv/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
