from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.projects import get_project_or_404
from app.database.database import get_db
from app.models.models import RiskScore
from app.schemas.schemas import RiskScoreRead

router = APIRouter(prefix="/api/projects/{project_id}/risk", tags=["Risk scores"])


@router.get("", response_model=RiskScoreRead)
def latest_risk_score(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    score = db.scalars(select(RiskScore).where(RiskScore.project_id == project_id).order_by(RiskScore.computed_at.desc()).limit(1)).first()
    if score is None:
        raise HTTPException(status_code=404, detail="No risk score found for this project")
    return score
