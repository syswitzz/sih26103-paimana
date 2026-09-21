"""Milestone autogeneration from the project schedule data already in the DB."""
from datetime import timedelta

from sqlalchemy import func, select

from app.models.models import Milestone, ProgressReport, Project


def milestone_status(progress: float, milestone_percent: int) -> str:
    if progress >= milestone_percent:
        return "COMPLETED"
    if progress >= max(0, milestone_percent - 10):
        return "IN_PROGRESS"
    return "PLANNED"


def build_milestones(project, latest_progress) -> list[Milestone]:
    progress = float(latest_progress.physical_progress_pct if latest_progress else 0)
    progress = max(0, min(progress, 100))

    start = project.start_date
    end = project.planned_end_date
    total_days = max((end - start).days, 0)

    rows = [
        Milestone(
            project_id=project.project_id,
            name="Project Sanction",
            planned_date=start,
            status="COMPLETED",
            sequence_no=1,
        ),
    ]

    for index, pct in enumerate((25, 50, 75), start=2):
        target_date = start + timedelta(days=int(total_days * pct / 100))
        rows.append(
            Milestone(
                project_id=project.project_id,
                name=f"{pct}% Physical Progress",
                planned_date=target_date,
                status=milestone_status(progress, pct),
                sequence_no=index,
            )
        )

    rows.append(
        Milestone(
            project_id=project.project_id,
            name="100% / Commissioning",
            planned_date=end,
            status="COMPLETED" if progress >= 100 else "PLANNED",
            sequence_no=5,
        )
    )

    return rows


def ensure_milestones(db) -> int:
    if db.scalar(select(func.count(Milestone.milestone_id))):
        return 0

    created = 0
    for project in db.scalars(select(Project)):
        latest_progress = db.scalars(
            select(ProgressReport)
            .where(ProgressReport.project_id == project.project_id)
            .order_by(ProgressReport.report_date.desc())
            .limit(1)
        ).first()
        db.add_all(build_milestones(project, latest_progress))
        created += 5

    db.commit()
    return created