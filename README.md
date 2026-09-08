# Setup

## Prerequisites

- Git
- Node.js 20.19+ and npm (Vite 8 / React 19)
- Python 3.12 (managed by uv)
- uv 0.9+
- PostgreSQL (local install)

## 1. Clone Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

The repository root contains three top-level directories: `backend/`, `frontend/`, and `ml/`.

## 2. PostgreSQL Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Verify it is running
sudo systemctl status postgresql --no-pager

# Create the paimana database
sudo -u postgres createdb paimana

# (Optional) Set a password on the postgres superuser, or create a dedicated role
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'CHANGE_ME';"

# Verify the database exists
sudo -u postgres psql -d paimana -c "SELECT 1;"
```

The connection credentials above must match `DATABASE_URL` in `backend/.env` (see Section 3). The role used in `DATABASE_URL` needs access to the `paimana` database.

## 3. Backend Setup

```bash
cd backend
uv sync
```

The backend reads configuration from `backend/.env`. Create it if it does not exist yet, based on the following template (use your own password, not a real one from the repository):

```dotenv
# PostgreSQL connection string
DATABASE_URL=postgresql+psycopg://postgres:CHANGE_ME@localhost:5432/paimana

# Comma-separated browser origins. Do not include a trailing slash.
CORS_ORIGINS=http://localhost:5173
ENVIRONMENT=development

# Paths are relative to the repository root unless absolute.
PROJECT_DATASET_PATH=../ml/data/Projects_Report.csv
ML_COST_MODEL_PATH=../ml/models/cost_model.pkl
ML_DELAY_MODEL_PATH=../ml/models/delay_model.pkl
ML_MODEL_VERSION=sih-rf-v1
```

`DATABASE_URL` format: `postgresql+psycopg://USER:PASSWORD@HOST:PORT/paimana`.

## 4. Database Migration

```bash
cd backend
uv run alembic upgrade head
```

This creates all tables (and the `project_overview` view) in the `paimana` database.

## 5. Import Dataset

```bash
cd backend
uv run python import_projects.py
```

This reads `ml/data/Projects_Report.csv`, upserts all projects and progress reports, derives `State`/`District`, and computes and persists a real ML risk score (`RiskScore`) for every project.

Re-running safely without wiping existing data:

```bash
uv run python import_projects.py --append
```

## 6. Start Backend

```bash
cd backend
uv run uvicorn app.main:app --reload
```

- Backend URL: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## 7. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- Frontend URL: http://localhost:5173

## 8. ML

- Models: `ml/models/cost_model.pkl`, `ml/models/delay_model.pkl`
- Dataset: `ml/data/Projects_Report.csv`
- Notebook: `ml/notebooks/risk_pridiction.ipynb`
- The backend loads the `.pkl` models automatically through `App.services.ml`; no separate ML server is required.

## 9. Full Startup Order

Run each command in its own terminal.

Terminal 1 — PostgreSQL:

```bash
sudo systemctl start postgresql
```

Terminal 2 — Backend (run once before first start: `uv run alembic upgrade head` and `uv run python import_projects.py`):

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Terminal 3 — Frontend:

```bash
cd frontend
npm install
npm run dev
```

## 10. Common Errors

| Error | Fix |
| --- | --- |
| `Is the server running on host "localhost"` / connection refused | Start PostgreSQL: `sudo systemctl start postgresql` |
| `database "paimana" does not exist` | Create it: `sudo -u postgres createdb paimana` |
| `password authentication failed` | Set the DB role password: `sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'CHANGE_ME';"` and update `DATABASE_URL` in `backend/.env` |
| `relation "projects" does not exist` | Run migrations: `cd backend && uv run alembic upgrade head` |
| Frontend fails to install/build | Use Node 20.19+ and reinstall: `cd frontend && rm -rf node_modules package-lock.json && npm install` |
| `joblib`/model file not found at startup | Confirm `ml/models/cost_model.pkl` and `ml/models/delay_model.pkl` exist and match `ML_COST_MODEL_PATH` / `ML_DELAY_MODEL_PATH` in `backend/.env` |