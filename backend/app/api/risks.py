from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.projects import get_project_or_404
from app.database.database import get_db
from app.models.models import ProgressReport, RiskScore
from app.schemas.schemas import RiskScoreRead
from app.services.ml import predict

router = APIRouter(prefix="/api/projects/{project_id}/risk", tags=["Risk scores"])


@router.get("", response_model=RiskScoreRead)
def latest_risk_score(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    score = db.scalars(select(RiskScore).where(RiskScore.project_id == project_id).order_by(RiskScore.computed_at.desc()).limit(1)).first()
    if score is None:
        raise HTTPException(status_code=404, detail="No risk score found for this project")
    return score


@router.post("/predict", response_model=RiskScoreRead, status_code=201)
def predict_risk(project_id: int, db: Session = Depends(get_db)):
    project = get_project_or_404(project_id, db)
    progress = db.scalars(
        select(ProgressReport)
        .where(ProgressReport.project_id == project_id)
        .order_by(ProgressReport.report_date.desc())
        .limit(1)
    ).first()
    probabilities = predict(project, progress)
    cost_probability = probabilities["cost_overrun_probability"]
    delay_probability = probabilities["delay_probability"]
    risk_score = (cost_probability + delay_probability) * 50
    risk_level = "HIGH" if risk_score >= 67 else "MEDIUM" if risk_score >= 34 else "LOW"
    score = RiskScore(
        project_id=project_id,
        health_score=max(0, 100 - risk_score),
        risk_score=risk_score,
        risk_level=risk_level,
        delay_probability=delay_probability,
        cost_overrun_probability=cost_probability,
        cost_overrun_estimate=max(0, cost_probability - 0.5) * float(project.revised_cost or project.sanctioned_cost),
        component_breakdown={"delay": delay_probability, "cost_overrun": cost_probability},
        model_version="sih-rf-v1",
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    return score
