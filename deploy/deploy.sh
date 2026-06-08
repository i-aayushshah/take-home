#!/usr/bin/env bash
# Pull prebuilt images from ghcr.io and restart TechKraft on the Azure VM.
set -euo pipefail

APP_DIR="${VM_APP_DIR:-/srv/techkraft}"
COMPOSE_FILE="docker-compose.prod.yml"

cd "$APP_DIR"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

echo "==> TechKraft deploy — $(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [ ! -f .env ]; then
  echo "ERROR: Missing $APP_DIR/.env — copy .env.example and configure it first."
  exit 1
fi

echo "==> Pulling latest compose + scripts..."
git pull --ff-only origin main || git pull --ff-only

echo "==> Pulling Docker images (no build on VM)..."
docker compose -f "$COMPOSE_FILE" pull

echo "==> Starting database and Redis..."
docker compose -f "$COMPOSE_FILE" up -d db redis

echo "==> Waiting for PostgreSQL..."
for i in $(seq 1 30); do
  if docker compose -f "$COMPOSE_FILE" exec -T db pg_isready -U "${POSTGRES_USER:-postgres}" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo "==> Running migrations..."
docker compose -f "$COMPOSE_FILE" run --rm --no-deps backend uv run alembic upgrade head

if [ "${RUN_SEED_ON_DEPLOY:-false}" = "true" ]; then
  echo "==> Seeding database..."
  docker compose -f "$COMPOSE_FILE" run --rm --no-deps backend uv run python -m seed
fi

echo "==> Starting all services..."
docker compose -f "$COMPOSE_FILE" up -d

echo "==> Health checks..."
for i in $(seq 1 20); do
  if curl -sf http://127.0.0.1/health >/dev/null 2>&1; then
    echo "  ✓ Backend is healthy"
    break
  fi
  sleep 3
done

if curl -sf http://127.0.0.1/ >/dev/null 2>&1; then
  echo "  ✓ Frontend is healthy"
else
  echo "  ! Frontend health check failed — check: docker compose -f $COMPOSE_FILE logs frontend"
fi

echo "==> ✓ Deploy complete"
docker compose -f "$COMPOSE_FILE" ps
