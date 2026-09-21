from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, dashboard, milestones, progress, projects, risks
from app.config import settings
from app.database.database import SessionLocal
from app.services.milestones import ensure_milestones
import app.models.models  # noqa: F401 - registers ORM models


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        count = ensure_milestones(db)
        if count:
            print(f"Populated {count} milestones.")
    except Exception as exc:  # never block startup on a backfill failure
        print(f"Milestone backfill skipped: {exc}")
    finally:
        db.close()
    yield


app = FastAPI(title="PAIMANA AI API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://paimana-frontend-w61j.onrender.com"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(projects.router)
app.include_router(milestones.router)
app.include_router(progress.router)
app.include_router(risks.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
