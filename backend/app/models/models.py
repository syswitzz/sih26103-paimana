from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Project(Base):
    __tablename__ = "projects"
    project_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str] = mapped_column(String(100), nullable=False)
    ministry: Mapped[str] = mapped_column(String(150), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    sanctioned_cost: Mapped[float] = mapped_column(Float, nullable=False)
    revised_cost: Mapped[float | None] = mapped_column(Float)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    current_status: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bucket: Mapped[str] = mapped_column(String(50), nullable=False)
    milestones: Mapped[list["Milestone"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    progress_reports: Mapped[list["ProgressReport"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    risk_scores: Mapped[list["RiskScore"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Milestone(Base):
    __tablename__ = "milestones"
    milestone_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    planned_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    dependency_milestone_id: Mapped[int | None] = mapped_column(ForeignKey("milestones.milestone_id"))
    project: Mapped[Project] = relationship(back_populates="milestones")
    dependency: Mapped["Milestone | None"] = relationship(remote_side="Milestone.milestone_id")


class ProgressReport(Base):
    __tablename__ = "progress_reports"
    report_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    physical_progress_pct: Mapped[float] = mapped_column(Float, nullable=False)
    expenditure_cumulative: Mapped[float] = mapped_column(Float, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)
    project: Mapped[Project] = relationship(back_populates="progress_reports")


class RiskScore(Base):
    __tablename__ = "risk_scores"
    score_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    health_score: Mapped[float] = mapped_column(Float, nullable=False)
    delay_probability: Mapped[float] = mapped_column(Float, nullable=False)
    cost_overrun_estimate: Mapped[float] = mapped_column(Float, nullable=False)
    component_breakdown: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    project: Mapped[Project] = relationship(back_populates="risk_scores")


class Alert(Base):
    __tablename__ = "alerts"
    alert_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
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
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.alert_id"), nullable=False)
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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    user: Mapped[User] = relationship(back_populates="audit_logs")
