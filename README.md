# TechKraft Candidate Scoring Dashboard

Internal candidate scoring and review dashboard for TechKraft's recruitment workflow.

## Stack

- **Backend:** FastAPI, SQLAlchemy 2.x (async), Alembic, PostgreSQL, Redis, uv
- **Frontend:** React 18, Vite 5, Tailwind CSS, Zustand, TanStack Query
- **Infra:** Docker Compose

## How to Run Locally

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended), **or**
- Python 3.11+, [uv](https://docs.astral.sh/uv/), Node.js 22+, PostgreSQL 16, Redis 7

### Environment variables

Database connection is built from individual `POSTGRES_*` variables (see `.env.example`):

```env
POSTGRES_DB=take-home
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

- **Local backend** (no Docker): use `POSTGRES_HOST=localhost`
- **Docker Compose**: `.env.example` uses `POSTGRES_HOST=db`; the backend service overrides host to `db` automatically

### Option A — Docker Compose (recommended)

```bash
# 1. Copy environment file and set your password
cp .env.example .env

# 2. Start all services (postgres, redis, backend, frontend)
docker-compose up --build
```

| Service   | URL |
|-----------|-----|
| Backend API | http://localhost:8000 |
| Frontend    | http://localhost:5173 |
| Health check | http://localhost:8000/health |

Run database migrations (after containers are up):

```bash
docker compose exec backend uv run alembic upgrade head
```

Stop services:

```bash
docker-compose down
```

### Option B — Run backend & frontend without Docker

**1. Start PostgreSQL and Redis** (or use Docker for only those services):

```bash
docker compose up db redis -d
```

**2. Backend**

```bash
cp .env.example .env
# Set POSTGRES_HOST=localhost and your POSTGRES_PASSWORD in .env
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**3. Frontend** (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the Vite dev server proxies API calls to `VITE_API_URL` (default `http://localhost:8000` in `.env`).

### Optional — GitHub AI summaries

Add your GitHub token to `.env` for live AI summaries (Phase 03):

```env
GITHUB_TOKEN=ghp_your_token_here
AI_SUMMARY_FALLBACK_MOCK=false
```

Without a token, the API falls back to a mock summary generator.
