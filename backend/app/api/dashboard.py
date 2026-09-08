from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.locations import UNSPECIFIED
from app.models.models import Alert, Project, ProgressReport, RiskScore

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    latest_score_ids = select(func.max(RiskScore.score_id)).group_by(RiskScore.project_id)
    latest = select(RiskScore).where(RiskScore.score_id.in_(latest_score_ids)).subquery()
    total_sanctioned = db.scalar(select(func.coalesce(func.sum(Project.sanctioned_cost), 0))) or 0
    total_revised = db.scalar(select(func.coalesce(func.sum(func.coalesce(Project.revised_cost, Project.sanctioned_cost)), 0))) or 0
    latest_progress = select(func.max(ProgressReport.report_id)).group_by(ProgressReport.project_id).subquery()
    average_progress = db.scalar(select(func.avg(ProgressReport.physical_progress_pct)).where(ProgressReport.report_id.in_(select(latest_progress.c.max))))
    return {
        "total_projects": db.scalar(select(func.count()).select_from(Project)) or 0,
        "total_sanctioned_cost": total_sanctioned,
        "total_revised_cost": total_revised,
        "average_physical_progress": average_progress,
        "high_risk_projects": db.scalar(select(func.count()).select_from(latest).where(latest.c.delay_probability >= 0.67)) or 0,
        "medium_risk_projects": db.scalar(select(func.count()).select_from(latest).where(latest.c.delay_probability >= 0.34, latest.c.delay_probability < 0.67)) or 0,
        "low_risk_projects": db.scalar(select(func.count()).select_from(latest).where(latest.c.delay_probability < 0.34)) or 0,
        "open_alerts": db.scalar(select(func.count()).select_from(Alert).where(Alert.status == "OPEN")) or 0,
    }


@router.get("/state-risks")
def state_risks(db: Session = Depends(get_db)):
    latest_score_ids = select(func.max(RiskScore.score_id)).group_by(RiskScore.project_id).subquery()
    latest = select(RiskScore).where(RiskScore.score_id.in_(select(latest_score_ids.c.max))).subquery()
    rows = db.execute(
        select(
            Project.state,
            func.count(Project.project_id),
            func.avg(latest.c.risk_score),
        )
        .outerjoin(latest, latest.c.project_id == Project.project_id)
        .where(Project.state != UNSPECIFIED)
        .group_by(Project.state)
        .order_by(Project.state)
    )
    result = []
    for state, project_count, average_risk_score in rows:
        score = float(average_risk_score) if average_risk_score is not None else None
        level = "HIGH" if score is not None and score >= 67 else "MEDIUM" if score is not None and score >= 34 else "LOW" if score is not None else None
        result.append({"state": state, "project_count": project_count, "average_risk_score": average_risk_score, "risk_level": level})
    return result
