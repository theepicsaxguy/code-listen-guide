# syntax=docker/dockerfile:1.19

ARG PYTHON_VERSION=3.14.0-slim
ARG NODE_VERSION=22.21.0-bookworm-slim
ARG VITE_API_BASE_PATH=/api/v1

FROM node:${NODE_VERSION} AS frontend-build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html tsconfig.json tsconfig.node.json tsconfig.app.json vite.config.ts postcss.config.js tailwind.config.ts eslint.config.js components.json ./
COPY public ./public
COPY src ./src
ENV VITE_API_BASE_PATH=${VITE_API_BASE_PATH}
RUN npm run build
ENV NODE_ENV=production

FROM python:${PYTHON_VERSION} AS wheels
WORKDIR /wheels
# Install build deps for compiling wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libssl-dev \
        libffi-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.runtime.txt ./requirements.txt
# Build wheels for all requirements into /wheels
# Use BuildKit cache mount for pip cache so wheels are only rebuilt when requirements.txt changes.
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip wheel setuptools && \
    python -m pip wheel --no-deps --wheel-dir=/wheels -r requirements.txt || true

FROM python:${PYTHON_VERSION} AS backend-build
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
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
# Copy requirements and install using a pre-built wheelhouse so rebuilds only re-run when requirements change.
# The `wheels` stage below builds wheels for the requirements; copying them from that stage
# means this layer is only invalidated when `backend/requirements.runtime.txt` changes.
COPY backend/requirements.runtime.txt ./requirements.txt
# Create virtualenv and upgrade pip
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip
# Copy pre-built wheels from the wheels stage and install from them (no network unless needed)
COPY --from=wheels /wheels /wheels
# Use BuildKit cache mount for pip install to reuse built artifacts when possible
RUN --mount=type=cache,target=/root/.cache/pip \
    /opt/venv/bin/pip install --find-links=/wheels -r requirements.txt
COPY backend ./backend

FROM python:${PYTHON_VERSION} AS production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
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
RUN groupadd --system app \
    && useradd --system --gid app --home /app --create-home --shell /usr/sbin/nologin app
WORKDIR /app
COPY --from=backend-build --chown=app:app /opt/venv /opt/venv
COPY --from=backend-build --chown=app:app /app/backend /app/backend
COPY --from=frontend-build --chown=app:app /app/dist /app/backend/frontend_dist
USER app
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
