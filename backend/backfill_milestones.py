"""Backfill the `milestones` table from dates already present in `projects`.

Creates five milestones per project (sanction, 25%/50%/75% progress,
commissioning) derived from start_date and planned_end_date, with status
computed from the latest physical progress on record.

Useful as a one-off job against a remote database whose app is already
deployed (see app.main lifespan for the automatic startup equivalent).
"""
from app.database.database import SessionLocal
from app.models.models import Milestone
from app.services.milestones import ensure_milestones
from sqlalchemy import delete


def main() -> int:
    db = SessionLocal()
    try:
        db.execute(delete(Milestone))
        db.commit()
        created = ensure_milestones(db)
        print(f"Backfilled {created} milestones.")
        return created
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()