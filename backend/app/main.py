from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, dashboard, milestones, progress, projects, risks
from app.config import settings
import app.models.models  # noqa: F401 - registers ORM models


app = FastAPI(title="PAIMANA AI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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
