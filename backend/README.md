# PAIMANA AI backend

PAIMANA AI is a Smart India Hackathon prototype for monitoring infrastructure projects and surfacing early-warning risks. This backend is intentionally a small, readable FastAPI and PostgreSQL foundation.

## Stack

Python 3.11+, FastAPI, SQLAlchemy 2.x, Pydantic, PostgreSQL, Psycopg, and Uvicorn.

## Run locally

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt

# Create the PostgreSQL database once (adjust the role if needed)
createdb paimana

# Configure a non-default connection if required
export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/paimana'

python seed.py
uvicorn app.main:app --reload
```

The connection string is read from `DATABASE_URL`; see `.env.example` for the default local value. The target PostgreSQL database must exist, while the application creates all tables automatically at startup. `seed.py` adds 12 clearly synthetic/demo projects and associated records; it is safe to run repeatedly. API documentation is at [http://localhost:8000/docs](http://localhost:8000/docs).

## Endpoints

- `GET`, `POST` `/api/projects`; `GET /api/projects/{project_id}` (list filters: `ministry`, `sector`, `state`, `status`)
- `GET`, `POST` `/api/projects/{project_id}/milestones`
- `GET`, `POST` `/api/projects/{project_id}/progress`
- `GET /api/projects/{project_id}/risk` (latest score)
- `GET /api/alerts`; `GET`, `POST` `/api/projects/{project_id}/alerts` (filters: `severity`, `status`, `alert_type`)
- `GET /api/dashboard/summary`; `GET /health`

## Tables

`projects`, `milestones`, `progress_reports`, `risk_scores`, `alerts`, `interventions`, `users`, and `audit_log`.
