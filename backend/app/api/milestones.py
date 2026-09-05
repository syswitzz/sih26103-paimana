from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.projects import get_project_or_404
from app.database.database import get_db
from app.models.models import Milestone
from app.schemas.schemas import MilestoneCreate, MilestoneRead

router = APIRouter(prefix="/api/projects/{project_id}/milestones", tags=["Milestones"])


@router.get("", response_model=list[MilestoneRead])
def list_milestones(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    return db.scalars(select(Milestone).where(Milestone.project_id == project_id).order_by(Milestone.sequence_no)).all()


@router.post("", response_model=MilestoneRead, status_code=201)
def create_milestone(project_id: int, payload: MilestoneCreate, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    if payload.dependency_milestone_id and db.get(Milestone, payload.dependency_milestone_id) is None:
        raise HTTPException(status_code=400, detail="Dependency milestone not found")
    milestone = Milestone(project_id=project_id, **payload.model_dump())
    db.add(milestone); db.commit(); db.refresh(milestone)
    return milestone
