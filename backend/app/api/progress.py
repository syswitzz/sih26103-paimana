from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.projects import get_project_or_404
from app.database.database import get_db
from app.models.models import ProgressReport
from app.schemas.schemas import ProgressReportCreate, ProgressReportRead

router = APIRouter(prefix="/api/projects/{project_id}/progress", tags=["Progress"])


@router.get("", response_model=list[ProgressReportRead])
def list_progress(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    return db.scalars(select(ProgressReport).where(ProgressReport.project_id == project_id).order_by(ProgressReport.report_date.desc())).all()


@router.post("", response_model=ProgressReportRead, status_code=201)
def create_progress(project_id: int, payload: ProgressReportCreate, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    report = ProgressReport(project_id=project_id, **payload.model_dump())
    db.add(report); db.commit(); db.refresh(report)
    return report
