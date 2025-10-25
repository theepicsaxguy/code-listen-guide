# syntax=docker/dockerfile:1.19

ARG PYTHON_VERSION=3.11.11-slim
ARG NODE_VERSION=22.12.0-bookworm-slim
ARG VITE_API_BASE_URL=/api/v1

FROM node:${NODE_VERSION} AS frontend-build
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json ./
RUN npm ci
COPY tsconfig.json tsconfig.node.json tsconfig.app.json vite.config.ts postcss.config.js tailwind.config.ts eslint.config.js components.json ./
COPY public ./public
COPY src ./src
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

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
COPY backend/requirements.runtime.txt ./requirements.txt
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
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
