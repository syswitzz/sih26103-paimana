from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.database.database import SessionLocal, get_db
from app.locations import UNSPECIFIED
from app.models.models import ProgressReport, Project, RiskScore
from app.schemas.schemas import ProjectCreate, ProjectListItem, ProjectRead, RiskScoreRead
from app.services.risks import build_risk_score

router = APIRouter(prefix="/api/projects", tags=["Projects"])

# In-memory job tracking for the batch prediction action.
# Suitable for the single-process development/demo backend.
_predict_job = {
    "status": "idle",  # idle | running | done | error
    "total": 0,
    "updated": 0,
    "error": None,
    "started_at": None,
    "finished_at": None,
}


def _run_all_predictions():
    """Compute and persist a risk score for every project that is still missing one."""
    try:
        _predict_job.update(status="running", error=None, started_at=datetime.utcnow().isoformat())
        db = SessionLocal()
        try:
            scored = select(RiskScore.project_id)
            projects = db.scalars(
                select(Project)
                .where(~exists(scored.where(RiskScore.project_id == Project.project_id)))
                .order_by(Project.project_id)
            ).all()
            _predict_job["total"] = len(projects)
            updated = 0
            for project in projects:
                progress = db.scalars(
                    select(ProgressReport)
                    .where(ProgressReport.project_id == project.project_id)
                    .order_by(ProgressReport.report_date.desc())
                    .limit(1)
                ).first()
                db.add(build_risk_score(project, progress))
                updated += 1
            db.commit()
            _predict_job["updated"] = updated
            _predict_job["status"] = "done"
        finally:
            db.close()
    except Exception as exc:  # pragma: no cover - defensive
        _predict_job["status"] = "error"
        _predict_job["error"] = str(exc)
    finally:
        _predict_job["finished_at"] = datetime.utcnow().isoformat()


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


@router.post("/risk/predict", status_code=202)
def predict_all_risks(background_tasks: BackgroundTasks):
    """Queue a background run that computes risk scores for projects still missing one."""
    if _predict_job["status"] == "running":
        raise HTTPException(status_code=409, detail="A risk prediction run is already in progress")
    background_tasks.add_task(_run_all_predictions)
    return {"status": "started"}


@router.get("/risk/predict/status")
def predict_all_risks_status():
    """Check the progress of the batch risk prediction job."""
    return {
        "status": _predict_job["status"],
        "total": _predict_job["total"],
        "updated": _predict_job["updated"],
        "error": _predict_job["error"],
        "started_at": _predict_job["started_at"],
        "finished_at": _predict_job["finished_at"],
    }


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
