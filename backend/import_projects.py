"""Import the primary PAIMANA project dataset into PostgreSQL."""
import argparse
import csv
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import delete, select

from app.config import settings
from app.database.database import SessionLocal
from app.models.models import AuditLog, Alert, Intervention, Milestone, ProgressReport, Project, RiskScore, User


DATE_FORMAT = "%d-%m-%Y"
UNKNOWN = "Not Specified"


def text(value: str | None, limit: int | None = None) -> str:
    value = (value or "").strip() or UNKNOWN
    return value[:limit] if limit else value


def decimal(value: str | None, default: Decimal = Decimal("0")) -> Decimal:
    raw = (value or "").strip().replace(",", "")
    return Decimal(raw) if raw else default


def parse_date(value: str | None) -> date | None:
    raw = (value or "").strip()
    if not raw:
        return None
    parsed = datetime.strptime(raw, DATE_FORMAT).date()
    return None if parsed.year < 2000 else parsed


def map_row(row: dict[str, str]) -> tuple[dict, date, Decimal, Decimal]:
    sanctioned_cost = decimal(row["Original Cost\n(in cr.)"])
    revised_value = decimal(row["Revised Cost\n(in cr.)"])
    revised_cost = max(sanctioned_cost, revised_value) if revised_value > 0 else sanctioned_cost
    expenditure = max(decimal(row["Expenditure\n(in cr.)"]), Decimal("0"))
    progress = min(max(decimal(row["Physical Progress\n(in %)"]), Decimal("0")), Decimal("100"))

    original_commissioning = parse_date(row["Original\nDate of Commissioning"])
    revised_commissioning = parse_date(row["Revised\nDate of Commissioning"])
    start_date = parse_date(row["Sanction Date"]) or original_commissioning or date.today()
    planned_end = revised_commissioning or original_commissioning or start_date
    if planned_end < start_date:
        planned_end = original_commissioning if original_commissioning and original_commissioning >= start_date else start_date

    if progress >= 100:
        status = "COMPLETED"
    elif planned_end < date.today():
        status = "DELAYED"
    elif progress == 0:
        status = "PLANNING"
    else:
        status = "IN_PROGRESS"

    project = {
        "name": text(row["Project Name"], 255),
        "sector": text(row["Sector Name"], 100),
        "ministry": text(row["Line Ministry"], 150),
        "implementing_agency": text(row["Implementing Agency"], 200),
        "state": UNKNOWN,
        "district": UNKNOWN,
        "sanctioned_cost": sanctioned_cost,
        "revised_cost": revised_cost,
        "start_date": start_date,
        "planned_end_date": planned_end,
        "current_status": status,
        "category": "Infrastructure",
    }
    return project, date.today(), expenditure, progress


def clear_primary_data(db) -> None:
    for model in (Intervention, AuditLog, Alert, RiskScore, ProgressReport, Milestone, Project, User):
        db.execute(delete(model))
    db.flush()


def import_dataset(replace: bool = True) -> int:
    with settings.dataset_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    db = SessionLocal()
    try:
        if replace:
            clear_primary_data(db)

        existing = {
            (project.name, project.ministry, project.start_date): project
            for project in db.scalars(select(Project)).all()
        }
        imported = 0
        for row in rows:
            project_values, report_date, expenditure, progress = map_row(row)
            key = (project_values["name"], project_values["ministry"], project_values["start_date"])
            project = existing.get(key)
            if project is None:
                project = Project(**project_values)
                db.add(project)
                db.flush()
                existing[key] = project
            else:
                for field, value in project_values.items():
                    setattr(project, field, value)

            report = db.scalars(
                select(ProgressReport).where(
                    ProgressReport.project_id == project.project_id,
                    ProgressReport.report_date == report_date,
                )
            ).first()
            if report is None:
                db.add(ProgressReport(
                    project_id=project.project_id,
                    report_date=report_date,
                    physical_progress_pct=progress,
                    expenditure_cumulative=expenditure,
                    remarks="Imported from Projects_Report.csv.",
                ))
            else:
                report.physical_progress_pct = progress
                report.expenditure_cumulative = expenditure
                report.remarks = "Imported from Projects_Report.csv."
            imported += 1

        db.commit()
        return imported
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--append", action="store_true", help="Upsert rows without clearing existing projects")
    args = parser.parse_args()
    count = import_dataset(replace=not args.append)
    print(f"Imported {count} CSV rows from {settings.dataset_path}")


if __name__ == "__main__":
    main()
