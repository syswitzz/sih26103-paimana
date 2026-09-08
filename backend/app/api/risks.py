from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.projects import get_project_or_404
from app.database.database import get_db
from app.models.models import ProgressReport, RiskScore
from app.schemas.schemas import RiskScoreRead
from app.services.risks import build_risk_score

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
    score = build_risk_score(project, progress)
    db.add(score)
    db.commit()
    db.refresh(score)
    return score
