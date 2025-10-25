# syntax=docker/dockerfile:1.7

ARG PYTHON_VERSION=3.14-slim
ARG NODE_VERSION=20-bookworm-slim
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
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt ./requirements.txt
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY backend ./backend

FROM python:${PYTHON_VERSION} AS production
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        libxml2 \
        libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=backend-build /opt/venv /opt/venv
COPY --from=backend-build /app/backend /app/backend
COPY --from=frontend-build /app/dist /app/backend/frontend_dist
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
