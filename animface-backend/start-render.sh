#!/usr/bin/env bash
set -euo pipefail

echo "[start] preparing runtime directories"
mkdir -p uploads/originals uploads/animated uploads/thumbnails logs

echo "[start] launching celery worker in background"
celery -A app.workers.celery_app worker \
  --loglevel=info \
  --concurrency="${ANIME_WORKER_CONCURRENCY:-2}" \
  -Q anime_conversion &

echo "[start] launching api on port ${PORT:-8000}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
