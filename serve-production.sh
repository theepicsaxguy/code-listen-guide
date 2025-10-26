#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
UVICORN_WORKERS="${UVICORN_WORKERS:-4}"

if [ ! -d node_modules ]; then
  npm install
fi

npm run build

rm -rf backend/frontend_dist
mkdir -p backend/frontend_dist
cp -R dist/. backend/frontend_dist/

BACKEND_PID=""

cleanup() {
  if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    kill "$BACKEND_PID"
  fi
  if [ -n "$BACKEND_PID" ]; then
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

uvicorn backend.main:app \
  --host "$BACKEND_HOST" \
  --port "$BACKEND_PORT" \
  --workers "$UVICORN_WORKERS" &
BACKEND_PID=$!

wait "$BACKEND_PID"
