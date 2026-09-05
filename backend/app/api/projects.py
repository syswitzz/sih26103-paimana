from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import Project
from app.schemas.schemas import ProjectCreate, ProjectRead

router = APIRouter(prefix="/api/projects", tags=["Projects"])


def get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(
    ministry: str | None = None, sector: str | None = None, state: str | None = None,
    status: str | None = None, db: Session = Depends(get_db),
):
    statement = select(Project)
    for field, value in ((Project.ministry, ministry), (Project.sector, sector), (Project.state, state), (Project.current_status, status)):
        if value:
            statement = statement.where(field == value)
    return db.scalars(statement.order_by(Project.project_id)).all()


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
