# RecipeForge

GitHub for recipes. Recipes have commits, branches, forks, diffs, and history.

## Stack

- **Frontend:** Next.js, TypeScript, Tailwind CSS — http://localhost:3000
- **Backend:** FastAPI, SQLAlchemy 2.0, Alembic — http://localhost:8000
- **Database:** PostgreSQL 16 (Docker) — localhost:5432

## Run it

Prereqs: Docker, Python 3.12+, Node 20+, npm.

```bash
# 1. Start PostgreSQL
docker compose up -d

# 2. Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Verify

- Health check: `http://localhost:8000/api/health` → `{"status":"ok","db":"ok"}`
- App: `http://localhost:3000` → landing page with green "Backend connected" card

## Status

Phase 1 of 13 in flight — project foundation (Postgres + API skeleton + frontend shell).
Full roadmap: [agents/PLAN.md](agents/PLAN.md)