from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import Alert, Project, RiskScore

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    latest_score_ids = select(func.max(RiskScore.score_id)).group_by(RiskScore.project_id)
    latest = select(RiskScore).where(RiskScore.score_id.in_(latest_score_ids)).subquery()
    return {
        "total_projects": db.scalar(select(func.count()).select_from(Project)) or 0,
        "high_risk_projects": db.scalar(select(func.count()).select_from(latest).where(latest.c.delay_probability >= 0.67)) or 0,
        "medium_risk_projects": db.scalar(select(func.count()).select_from(latest).where(latest.c.delay_probability >= 0.34, latest.c.delay_probability < 0.67)) or 0,
        "low_risk_projects": db.scalar(select(func.count()).select_from(latest).where(latest.c.delay_probability < 0.34)) or 0,
        "open_alerts": db.scalar(select(func.count()).select_from(Alert).where(Alert.status == "OPEN")) or 0,
    }
