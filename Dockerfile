# syntax=docker/dockerfile:1.19

ARG PYTHON_IMAGE=python:3.14.0-slim@sha256:4ed33101ee7ec299041cc41dd268dae17031184be94384b1ce7936dc4e5dead3
ARG NODE_IMAGE=node:22.21.0-bookworm-slim@sha256:f9f7f95dcf1f007b007c4dcd44ea8f7773f931b71dc79d57c216e731c87a090b
ARG NPM_VERSION=10.9.2
ARG VITE_API_BASE_PATH=/api/v1
ARG DEBIAN_RELEASE=bookworm
ARG DEBIAN_SNAPSHOT=20241103T000000Z
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
RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt \
    set -eux; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential=12.9 \
        python3-dev=3.11.2-1+b1 \
        libssl-dev=3.0.14-1~deb12u1 \
        libffi-dev=3.4.4-1 \
        libpq-dev=15.8-0+deb12u1; \
    rm -rf /var/lib/apt/lists/*
COPY backend/requirements.runtime.txt ./requirements.runtime.txt

# =============================================================================
# System Dependencies Stage (very rarely changes)
# =============================================================================
FROM python-base AS system-deps
ARG DEBIAN_RELEASE
ARG DEBIAN_SNAPSHOT
ARG SNAPSHOT_BASE_URL
ENV PYTHONDONTWRITEBYTECODE=1
RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt \
    set -eux; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ffmpeg=7:5.1.6-0+deb12u1 \
        build-essential=12.9 \
        libxml2-dev=2.9.14+dfsg-1.3~deb12u1 \
        libxslt1-dev=1.1.35-1 \
        zlib1g-dev=1:1.2.13.dfsg-1 \
        git=1:2.39.2-1.1 \
        cmake=3.25.1-1 \
        pkg-config=1.8.1-1 \
        libssl-dev=3.0.14-1~deb12u1 \
        libffi-dev=3.4.4-1 \
        libpq-dev=15.8-0+deb12u1 \
        curl=7.88.1-10+deb12u7; \
    rm -rf /var/lib/apt/lists/*

# =============================================================================
# Backend Dependencies Stage (cached)
# =============================================================================
FROM system-deps AS backend-deps
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY backend/requirements.runtime.txt backend/requirements.base.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    /opt/venv/bin/pip install --cache-dir /root/.cache/pip \
        pip==24.3.1 \
        wheel==0.45.0 \
        setuptools==75.3.0 && \
    /opt/venv/bin/pip install --require-hashes --cache-dir /root/.cache/pip -r requirements.runtime.txt

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
RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt \
    set -eux; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ffmpeg=7:5.1.6-0+deb12u1 \
        libxml2=2.9.14+dfsg-1.3~deb12u1 \
        libxslt1.1=1.1.35-1 \
        zlib1g=1:1.2.13.dfsg-1 \
        git=1:2.39.2-1.1 \
        curl=7.88.1-10+deb12u7 \
        libpq5=15.8-0+deb12u1; \
    rm -rf /var/lib/apt/lists/*

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
