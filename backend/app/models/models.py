from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import CheckConstraint, Computed, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint("sanctioned_cost > 0", name="projects_sanctioned_cost_positive"),
        CheckConstraint("revised_cost IS NULL OR revised_cost >= sanctioned_cost", name="projects_revised_cost_valid"),
        CheckConstraint("planned_end_date >= start_date", name="projects_date_order"),
        CheckConstraint("current_status IN ('PLANNING','IN_PROGRESS','DELAYED','COMPLETED','ON_HOLD')", name="projects_status_valid"),
        Index("idx_projects_search", "name"), Index("idx_projects_filters", "ministry", "sector", "state", "current_status"),
    )
    project_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str] = mapped_column(String(100), nullable=False)
    ministry: Mapped[str] = mapped_column(String(150), nullable=False)
    implementing_agency: Mapped[str] = mapped_column(String(200), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    sanctioned_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    revised_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    current_status: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bucket: Mapped[str] = mapped_column(String(20), Computed("CASE WHEN COALESCE(revised_cost, sanctioned_cost) < 500 THEN 'SMALL' WHEN COALESCE(revised_cost, sanctioned_cost) < 1000 THEN 'MEDIUM' ELSE 'LARGE' END", persisted=True), nullable=False)
    milestones: Mapped[list["Milestone"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    progress_reports: Mapped[list["ProgressReport"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    risk_scores: Mapped[list["RiskScore"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Milestone(Base):
    __tablename__ = "milestones"
    __table_args__ = (CheckConstraint("sequence_no > 0", name="milestones_sequence_positive"), CheckConstraint("status IN ('PLANNED','IN_PROGRESS','COMPLETED','DELAYED','CANCELLED')", name="milestones_status_valid"), Index("idx_milestones_project_sequence", "project_id", "sequence_no"))
    milestone_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    planned_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    dependency_milestone_id: Mapped[int | None] = mapped_column(ForeignKey("milestones.milestone_id", ondelete="SET NULL"))
    project: Mapped[Project] = relationship(back_populates="milestones")
    dependency: Mapped["Milestone | None"] = relationship(remote_side="Milestone.milestone_id")


class ProgressReport(Base):
    __tablename__ = "progress_reports"
    __table_args__ = (CheckConstraint("physical_progress_pct BETWEEN 0 AND 100", name="progress_pct_valid"), CheckConstraint("expenditure_cumulative >= 0", name="progress_expenditure_valid"), UniqueConstraint("project_id", "report_date", name="progress_reports_project_date_uq"), Index("idx_progress_project_date", "project_id", "report_date"))
    report_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id", ondelete="RESTRICT"), nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    physical_progress_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    expenditure_cumulative: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)
    project: Mapped[Project] = relationship(back_populates="progress_reports")


class RiskScore(Base):
    __tablename__ = "risk_scores"
    __table_args__ = (CheckConstraint("health_score BETWEEN 0 AND 100", name="risk_health_valid"), CheckConstraint("delay_probability BETWEEN 0 AND 1", name="risk_delay_valid"), CheckConstraint("cost_overrun_probability BETWEEN 0 AND 1", name="risk_cost_probability_valid"), CheckConstraint("risk_score BETWEEN 0 AND 100", name="risk_score_valid"), CheckConstraint("risk_level IN ('LOW','MEDIUM','HIGH')", name="risk_level_valid"), Index("idx_risk_project_computed", "project_id", "computed_at"))
    score_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id", ondelete="RESTRICT"), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    health_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    delay_probability: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    cost_overrun_probability: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    cost_overrun_estimate: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    component_breakdown: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    project: Mapped[Project] = relationship(back_populates="risk_scores")


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (CheckConstraint("severity IN ('CRITICAL','HIGH','MEDIUM','LOW')", name="alerts_severity_valid"), CheckConstraint("status IN ('OPEN','ACKNOWLEDGED','RESOLVED','DISMISSED')", name="alerts_status_valid"), Index("idx_alerts_project_generated", "project_id", "generated_at"))
    alert_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id", ondelete="RESTRICT"), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    explanation_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN")
    project: Mapped[Project] = relationship(back_populates="alerts")
    interventions: Mapped[list["Intervention"]] = relationship(back_populates="alert", cascade="all, delete-orphan")


class Intervention(Base):
    __tablename__ = "interventions"
    intervention_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.alert_id", ondelete="RESTRICT"), nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(String(150))
    action_taken: Mapped[str] = mapped_column(Text, nullable=False)
    action_date: Mapped[date] = mapped_column(Date, nullable=False)
    outcome_status: Mapped[str] = mapped_column(String(50), nullable=False)
    outcome_recorded_at: Mapped[datetime | None] = mapped_column(DateTime)
    alert: Mapped[Alert] = relationship(back_populates="interventions")


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    ministry_scope: Mapped[str | None] = mapped_column(String(150))
    state_scope: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")


class AuditLog(Base):
    __tablename__ = "audit_log"
    log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    user: Mapped[User] = relationship(back_populates="audit_logs")
