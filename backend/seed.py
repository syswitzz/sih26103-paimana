"""Populate the PAIMANA AI PostgreSQL database with synthetic demo data."""

'''
from datetime import UTC, date, datetime, timedelta

from app.database.database import SessionLocal
from app.models.models import Alert, AuditLog, Intervention, Milestone, ProgressReport, Project, RiskScore, User

PROJECTS = [
    ("Eastern Freight Corridor Package A", "Railways", "Ministry of Railways", "Bihar", "Munger", 2200, "IN_PROGRESS", 78, .71),
    ("National Highway Development Package B", "Roads", "Ministry of Road Transport", "Maharashtra", "Nashik", 1850, "DELAYED", 44, .84),
    ("Regional Water Supply Project C", "Water", "Ministry of Jal Shakti", "Rajasthan", "Ajmer", 640, "IN_PROGRESS", 62, .49),
    ("Solar Transmission Project D", "Power", "Ministry of Power", "Gujarat", "Kutch", 980, "IN_PROGRESS", 70, .28),
    ("Coastal Port Connectivity Project E", "Ports", "Ministry of Ports", "Odisha", "Kendrapara", 1500, "PLANNING", 12, .37),
    ("Metro Extension Package F", "Urban Transport", "Ministry of Housing", "Karnataka", "Bengaluru Urban", 3400, "DELAYED", 39, .76),
    ("Rural Digital Connectivity Project G", "Telecom", "Ministry of Communications", "Assam", "Kamrup", 410, "IN_PROGRESS", 66, .22),
    ("River Basin Restoration Project H", "Environment", "Ministry of Environment", "Uttar Pradesh", "Prayagraj", 720, "IN_PROGRESS", 54, .58),
    ("Industrial Logistics Hub Project I", "Logistics", "Ministry of Commerce", "Tamil Nadu", "Chennai", 1100, "COMPLETED", 100, .08),
    ("Mountain Tunnel Safety Upgrade J", "Roads", "Ministry of Road Transport", "Himachal Pradesh", "Kullu", 890, "DELAYED", 35, .81),
    ("Northern Irrigation Modernisation K", "Irrigation", "Ministry of Jal Shakti", "Punjab", "Ludhiana", 560, "IN_PROGRESS", 74, .31),
    ("City Waste Processing Project L", "Sanitation", "Ministry of Housing", "Telangana", "Hyderabad", 330, "IN_PROGRESS", 58, .52),
]


def main():
    db = SessionLocal()
    try:
        if db.query(Project).first():
            print("Database already contains projects; seed skipped.")
            return

        today = date.today()

        demo_user = User(name="Demo Officer", role="ADMIN", email="demo.officer@paimana.local")
        db.add(demo_user)
        db.flush()

        for index, (name, sector, ministry, state, district, cost, status, progress, risk) in enumerate(PROJECTS, 1):
            project = Project(
                name=name, sector=sector, ministry=ministry, implementing_agency="UNSPECIFIED", state=state, district=district,
                sanctioned_cost=cost, revised_cost=cost * (1.12 if risk >= .67 else 1.02),
                start_date=today - timedelta(days=600 - index * 20),
                planned_end_date=today + timedelta(days=365 + index * 20),
                current_status=status, category="Infrastructure",
            )
            db.add(project)
            db.flush()

            # First milestone is backdated to just after project start
            first_planned = project.start_date + timedelta(days=60)

            db.add_all([
                Milestone(project_id=project.project_id, name="Site preparation", planned_date=first_planned, actual_date=first_planned + timedelta(days=5), status="COMPLETED", sequence_no=1),
                Milestone(project_id=project.project_id, name="Core construction", planned_date=today + timedelta(days=90), status="IN_PROGRESS", sequence_no=2),
                ProgressReport(project_id=project.project_id, report_date=today, physical_progress_pct=progress, expenditure_cumulative=cost * progress / 100, remarks="Synthetic demo progress update."),
                RiskScore(project_id=project.project_id, computed_at=datetime.now(UTC).replace(tzinfo=None), health_score=round(100 - risk * 70), risk_score=round(risk * 100, 2), risk_level="HIGH" if risk >= .67 else "MEDIUM" if risk >= .34 else "LOW", delay_probability=risk, cost_overrun_probability=risk, cost_overrun_estimate=round(cost * max(0, risk - .2) * .2, 2), component_breakdown={"schedule": risk, "financial": round(min(1, risk * .85), 2), "progress": round(min(1, risk * .9), 2)}, model_version="seed-demo"),
            ])

            if risk >= .45:
                alert = Alert(project_id=project.project_id, alert_type="DELAY_RISK", severity="HIGH" if risk >= .67 else "MEDIUM", explanation_text="Synthetic demo alert based on the prototype risk score.", status="OPEN")
                db.add(alert)
                db.flush()
                db.add(Intervention(alert_id=alert.alert_id, assigned_to="Demo Officer", action_taken="Review project schedule and mitigation plan.", action_date=today, outcome_status="PENDING"))

        db.flush()
        # entity_id=0 is a sentinel here since this audit entry covers the whole
        # seeded dataset rather than a single project.
        db.add(AuditLog(user_id=demo_user.user_id, action_type="SEED", entity_type="PROJECT_DATASET", entity_id=0, details={"source": "synthetic_demo", "project_count": len(PROJECTS)}))
        db.commit()
        print(f"Seeded {len(PROJECTS)} synthetic demo projects plus users, alerts, interventions and audit data.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
'''


"""Populate PostgreSQL with the primary Projects_Report.csv dataset."""
from import_projects import import_dataset


if __name__ == "__main__":
    print(f"Imported {import_dataset(replace=True)} rows from the primary project dataset.")
