from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.projects import get_project_or_404
from app.database.database import get_db
from app.models.models import Alert
from app.schemas.schemas import AlertCreate, AlertRead

router = APIRouter(tags=["Alerts"])


@router.get("/api/alerts", response_model=list[AlertRead])
def list_alerts(severity: str | None = None, status: str | None = None, alert_type: str | None = None, db: Session = Depends(get_db)):
    statement = select(Alert)
    for field, value in ((Alert.severity, severity), (Alert.status, status), (Alert.alert_type, alert_type)):
        if value:
            statement = statement.where(field == value)
    return db.scalars(statement.order_by(Alert.generated_at.desc())).all()


@router.get("/api/projects/{project_id}/alerts", response_model=list[AlertRead])
def project_alerts(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    return db.scalars(select(Alert).where(Alert.project_id == project_id).order_by(Alert.generated_at.desc())).all()


@router.post("/api/projects/{project_id}/alerts", response_model=AlertRead, status_code=201)
def create_alert(project_id: int, payload: AlertCreate, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    alert = Alert(project_id=project_id, **payload.model_dump())
    db.add(alert); db.commit(); db.refresh(alert)
    return alert
