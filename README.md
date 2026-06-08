# TechKraft Candidate Scoring Dashboard

Internal candidate scoring and review dashboard for TechKraft's recruitment workflow.

## Stack

| Layer | Technologies |
|---|---|
| Backend | FastAPI, SQLAlchemy 2.x (async), Alembic, PostgreSQL, Redis, uv |
| Frontend | React 18, Vite, Tailwind CSS v4, Zustand, TanStack Query |
| Infra | Docker Compose |
| AI | GitHub Models API (`models.github.ai`) |

## Quick start (Docker Compose)

```bash
cp .env.example .env
# Edit POSTGRES_PASSWORD and other values as needed
docker compose up --build
```

In a second terminal, run migrations:

```bash
docker compose exec backend uv run alembic upgrade head
```

Optional seed (if the database is empty):

```bash
docker compose exec backend uv run python -m seed
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Health check | http://localhost:8000/health |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

**Demo admin login:** `admin@techkraft.com` / `admin12345`

Stop services:

```bash
docker compose down
```

## Local development (without full Docker)

### 1. Start PostgreSQL and Redis

```bash
docker compose up db redis -d
```

### 2. Backend

```bash
cp .env.example .env
# Set POSTGRES_HOST=localhost and your POSTGRES_PASSWORD
cd backend
uv sync
uv run alembic upgrade head
uv run python -m seed
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Environment variables

Database connection is built from `POSTGRES_*` variables (see `.env.example`):

```env
POSTGRES_DB=take-home
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost   # use "db" in Docker Compose
POSTGRES_PORT=5432
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=changeme
```

### GitHub token (AI summaries)

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Create a token with **`models:read`** scope (fine-grained or classic)
3. Add to `.env`:

```env
GITHUB_TOKEN=ghp_your_token_here
GITHUB_MODEL=openai/gpt-4o
AI_SUMMARY_FALLBACK_MOCK=false
```

Without a token (or with `AI_SUMMARY_FALLBACK_MOCK=true`), the API uses a mock summary generator for local development.

## API examples

```bash
# Register reviewer
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"reviewer@techkraft.com","password":"secret12345"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@techkraft.com","password":"admin12345"}'

# List candidates (replace TOKEN)
curl "http://localhost:8000/api/v1/candidates?status=new&limit=20" \
  -H "Authorization: Bearer TOKEN"

# Candidate detail
curl http://localhost:8000/api/v1/candidates/CANDIDATE_ID \
  -H "Authorization: Bearer TOKEN"

# Submit score
curl -X POST http://localhost:8000/api/v1/candidates/CANDIDATE_ID/scores \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"category":"technical","score":4,"note":"Strong fundamentals"}'

# Generate AI summary
curl -X POST http://localhost:8000/api/v1/candidates/CANDIDATE_ID/summary \
  -H "Authorization: Bearer TOKEN"
```

## Running tests

Tests use in-memory SQLite and fakeredis — no PostgreSQL or Redis required.

```bash
cd backend
uv sync --group dev
uv run pytest
```

Coverage includes:

- Candidate detail shape and role-filtered scores
- Score submission persistence
- SQL-level pagination totals (not Python-side filtering)
- Registration always creates `reviewer` role
- Login rate limiting (429)
- Soft delete returns 404
- AI summary text normalization

## Architecture notes

### SQL filtering fix (pagination `total`)

**Problem:** A naive implementation loads all candidates into Python, filters in memory, and returns `len(filtered)` as `total`. That breaks pagination — `total` does not match the database, offsets skip rows incorrectly, and memory grows with table size.

**Fix:** Compose `WHERE` clauses in SQLAlchemy (`status`, `role_applied`, `skill`, keyword on name/email), run a separate `COUNT(*)`, and apply `LIMIT`/`OFFSET` in the database. The list endpoint returns an accurate `total` for the active filter set.

### Vertical-slice structure

Each feature (auth, candidates) is organized as domain → application → infrastructure → presentation, with shared cross-cutting utilities in `app/shared/`.

## Architecture decision records

| # | Decision | Trade-off |
|---|---|---|
| 1 | PostgreSQL + vertical-slice DDD | More structure and testability vs. a flatter single-module layout |
| 2 | GitHub Models API for AI summaries | Real async external inference vs. a pure mock (mock remains available via env flag) |
| 3 | Zustand + TanStack Query | Auth in local persisted store; server state cached and invalidated via TanStack Query |
| 4 | Glass morphism UI (Tailwind v4) | Distinctive polished UI vs. additional CSS/design effort |

## Learning reflection

This project was a good exercise in wiring a full-stack recruitment workflow end-to-end — especially integrating the GitHub Models inference API (migrating from the deprecated Azure endpoint to `models.github.ai`) and building a glass morphism UI with Tailwind v4 utility patterns and custom component classes.

## Known limitations

- SSE streaming for AI summaries not implemented (see optional stretch goals)
- Rate limiter uses a fixed Redis window, not a sliding-window Lua script
- Docker frontend runs the Vite dev server, not a production nginx static build
- Skill filter uses JSON `contains` — behavior is PostgreSQL-specific

## Assignment requirements checklist

- [x] FastAPI backend with PostgreSQL and Redis
- [x] Candidate list with filters and SQL-backed pagination
- [x] Candidate detail with role-aware scores
- [x] Score submission API
- [x] AI summary generation (GitHub Models + mock fallback)
- [x] Admin internal notes and soft delete
- [x] React frontend with auth, list, and detail flows
- [x] Docker Compose for local development
- [x] pytest API tests
