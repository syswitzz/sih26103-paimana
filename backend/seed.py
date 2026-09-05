"""Populate the PAIMANA AI SQLite database with synthetic demo data."""
from datetime import UTC, date, datetime, timedelta

from app.database.database import Base, SessionLocal, engine
from app.models.models import Alert, Milestone, ProgressReport, Project, RiskScore

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
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Project).first():
            print("Database already contains projects; seed skipped.")
            return
        today = date.today()
        for index, (name, sector, ministry, state, district, cost, status, progress, risk) in enumerate(PROJECTS, 1):
            project = Project(name=name, sector=sector, ministry=ministry, state=state, district=district,
                sanctioned_cost=cost, revised_cost=cost * (1.12 if risk >= .67 else 1.02),
                start_date=today - timedelta(days=600 - index * 20), planned_end_date=today + timedelta(days=365 + index * 20),
                current_status=status, category="Infrastructure", size_bucket="Large" if cost >= 1000 else "Medium")
            db.add(project); db.flush()
            db.add_all([
                Milestone(project_id=project.project_id, name="Site preparation", planned_date=project.start_date + timedelta(days=60), actual_date=project.start_date + timedelta(days=65), status="COMPLETED", sequence_no=1),
                Milestone(project_id=project.project_id, name="Core construction", planned_date=today + timedelta(days=90), actual_date=None, status="IN_PROGRESS", sequence_no=2),
                ProgressReport(project_id=project.project_id, report_date=today, physical_progress_pct=progress, expenditure_cumulative=cost * progress / 100, remarks="Synthetic demo progress update."),
                RiskScore(project_id=project.project_id, computed_at=datetime.now(UTC), health_score=round(100 - risk * 70), delay_probability=risk, cost_overrun_estimate=round(cost * max(0, risk - .2) * .2, 2), component_breakdown={"schedule": risk, "financial": round(min(1, risk * .85), 2), "progress": round(min(1, risk * .9), 2)}),
            ])
            if risk >= .45:
                db.add(Alert(project_id=project.project_id, alert_type="DELAY_RISK", severity="HIGH" if risk >= .67 else "MEDIUM", explanation_text="Synthetic demo alert based on the prototype risk score.", status="OPEN"))
        db.commit()
        print(f"Seeded {len(PROJECTS)} synthetic demo projects.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
