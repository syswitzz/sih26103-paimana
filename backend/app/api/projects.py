from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.locations import UNSPECIFIED
from app.models.models import Project, RiskScore
from app.schemas.schemas import ProjectCreate, ProjectListItem, ProjectRead, RiskScoreRead

router = APIRouter(prefix="/api/projects", tags=["Projects"])


def get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=list[ProjectListItem])
def list_projects(
    name: str | None = None, ministry: str | None = None, sector: str | None = None, state: str | None = None,
    status: str | None = None, db: Session = Depends(get_db),
):
    statement = select(Project)
    if name:
        statement = statement.where(Project.name.ilike(f"%{name}%"))
    for field, value in ((Project.ministry, ministry), (Project.sector, sector), (Project.state, state), (Project.current_status, status)):
        if value:
            statement = statement.where(field == value)
    projects = db.scalars(statement.order_by(Project.project_id)).all()
    result = []
    for project in projects:
        latest_risk = db.scalars(
            select(RiskScore)
            .where(RiskScore.project_id == project.project_id)
            .order_by(RiskScore.computed_at.desc())
            .limit(1)
        ).first()
        result.append({
            "project_id": project.project_id,
            "name": project.name,
            "ministry": project.ministry,
            "sector": project.sector,
            "state": project.state,
            "district": project.district,
            "current_status": project.current_status,
            "size_bucket": project.size_bucket,
            "latest_risk": RiskScoreRead.model_validate(latest_risk) if latest_risk else None,
        })
    return result


@router.get("/sectors")
def list_sectors(db: Session = Depends(get_db)):
    return db.scalars(
        select(Project.sector).where(Project.sector != UNSPECIFIED).distinct().order_by(Project.sector)
    ).all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return get_project_or_404(project_id, db)


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    if payload.planned_end_date < payload.start_date:
        raise HTTPException(status_code=400, detail="planned_end_date must be on or after start_date")
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
