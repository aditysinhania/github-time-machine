# 🕰️ GitHub Time Machine

AI-powered repository intelligence platform. Point it at any public GitHub repo and get back ownership maps, risk hotspots, a health score, and an AI-generated evolution timeline — instead of scrolling through thousands of raw commits.

## Stack

| Layer | Tech |
|---|---|
| Frontend | React (Vite) · TypeScript · Tailwind · ShadCN-style UI · Recharts |
| Backend | FastAPI · SQLAlchemy (async) · GitPython · Pandas |
| Database | PostgreSQL + Alembic migrations |
| AI | Gemini or OpenAI (pluggable) |
| Deploy | Docker Compose · Railway · Render |

## Project Structure

```
github-time-machine/
├── backend/
│   ├── main.py                 # FastAPI app entry
│   ├── core/                   # config, security
│   ├── database/                # async engine, session, table init
│   ├── models/                  # Repository, Commit, Contributor, FileChange
│   ├── schemas/                 # Pydantic request/response shapes
│   ├── api/routes/               # repositories, contributors, timeline,
│   │                              hotspots, ownership, health, ai
│   ├── services/                 # git_service (clone+extract), ai_service
│   ├── analytics/                 # commit/contributor/hotspot/health analyzers
│   ├── alembic/                   # migrations (versioned schema)
│   ├── scripts/seed_demo.py        # populate DB with a demo analysis
│   └── tests/                       # pytest suite for analytics + API
├── frontend/
│   ├── src/api/                  # typed axios client
│   ├── src/components/ui/         # Button, Card, Badge, Tabs, Progress…
│   ├── src/components/dashboard/   # charts, KPI cards, chat panel, tabs
│   ├── src/hooks/                   # polling, fetch, zustand store
│   ├── src/pages/                    # Landing, Dashboard, Insights
│   └── src/types/api.ts               # mirrors backend schemas exactly
├── docker-compose.yml              # dev stack (hot reload)
├── docker-compose.prod.yml          # production overrides
├── render.yaml                       # Render blueprint
├── backend/railway.json               # Railway service config
├── .github/workflows/ci.yml            # tests on every push
└── Makefile                             # `make up`, `make migrate`, `make seed`…
```

## Quick Start (Docker)

```bash
git clone <your-fork-url> github-time-machine
cd github-time-machine

cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# edit backend/.env — add GEMINI_API_KEY or OPENAI_API_KEY

make up
# Frontend → http://localhost:5173
# Backend  → http://localhost:8000/docs
```

Apply migrations and load a demo repo:
```bash
make migrate
make seed              # analyzes pallets/flask by default
make seed url=https://github.com/expressjs/express
```

## Quick Start (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # point DATABASE_URL at a local Postgres
alembic upgrade head
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## How Analysis Works

1. `POST /api/v1/repositories/analyze` — accepts a GitHub URL, creates a `Repository` row with `status=pending`, and kicks off a background task. Returns immediately.
2. The background task clones the repo (`GitPython`), walks every commit, aggregates per-file and per-author stats, then runs four analyzers:
   - **CommitAnalyzer** — buckets commits by week/month/year, heuristically detects milestones from commit message keywords
   - **ContributorAnalyzer** — bus factor (commits needed to reach 50%), diversity (Shannon entropy over contribution shares), consistency (coefficient of variation across months), module ownership
   - **HotspotAnalyzer** — per-file risk score from change frequency, author spread, churn ratio, and a path-sensitivity bonus (auth/payment/config keywords)
   - **HealthAnalyzer** — weighted composite of the above four (30/25/25/20%) → 0–100 score and A–F grade
3. The frontend polls `GET /repositories/{id}` every 2s until `status` is `complete` or `failed`, then loads all five dashboard tabs in parallel.
4. The AI Insights page calls Gemini/OpenAI once (cached on the `Repository` row) for a structured summary, and supports free-form chat grounded in the same repo context.

## Testing

```bash
make test                     # full suite against dockerized Postgres
# or locally:
cd backend && pytest -v
```

The analytics modules (`commit_analyzer`, `contributor_analyzer`, `hotspot_analyzer`, `health_analyzer`) are pure-logic and unit-tested with fixed fixtures — no DB or network required. API smoke tests need a reachable Postgres and skip cleanly if one isn't available.

## Database Migrations

```bash
make migrate                                    # apply all pending migrations
make revision msg="add some_column"             # autogenerate a new one
make migrate-down                                 # roll back one step
```

The initial migration (`0001_initial_schema`) creates all four tables and exactly mirrors the SQLAlchemy models in `backend/models/`.

## Deployment

**Railway:** `backend/railway.json` configures the Docker build, health check, and start command. Add a Postgres plugin and set `DATABASE_URL`, `GEMINI_API_KEY`/`OPENAI_API_KEY` as env vars.

**Render:** `render.yaml` is a full blueprint — push it and Render provisions the Postgres database, backend web service, and frontend static site together. Set the two `sync: false` secrets (AI keys) in the dashboard after first deploy.

**Self-hosted:** `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build` runs the production profile (no hot reload, 4 uvicorn workers, resource limits).

## API Reference

Full interactive docs at `/docs` (Swagger) and `/redoc` once running. Summary:

```
POST   /api/v1/repositories/analyze
GET    /api/v1/repositories/
GET    /api/v1/repositories/{id}
DELETE /api/v1/repositories/{id}

GET    /api/v1/repositories/{id}/contributors
GET    /api/v1/repositories/{id}/timeline?granularity=week|month|year
GET    /api/v1/repositories/{id}/milestones
GET    /api/v1/repositories/{id}/hotspots?risk=high|medium|low
GET    /api/v1/repositories/{id}/ownership
GET    /api/v1/repositories/{id}/health

GET    /api/v1/repositories/{id}/ai/summary?refresh=false
POST   /api/v1/repositories/{id}/ai/chat
```

## Known Limitations

- Only public GitHub repositories are supported out of the box (set `GITHUB_TOKEN` in `.env` to raise rate limits or access private repos you have access to).
- Very large monorepos (100k+ commits) are capped at `MAX_COMMITS` (default 10,000) to bound memory and clone time — raise it in `.env` if needed.
- Milestone detection is keyword-heuristic, not LLM-based, to keep analysis fast and free of per-commit AI costs. The AI layer is reserved for the summary and chat features, which read already-computed stats rather than raw history.
