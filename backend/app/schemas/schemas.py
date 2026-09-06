from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sector: str
    ministry: str
    state: str
    district: str
    sanctioned_cost: float = Field(ge=0)
    revised_cost: float | None = Field(default=None, ge=0)
    start_date: date
    planned_end_date: date
    current_status: str
    category: str
    size_bucket: str


class ProjectRead(ProjectCreate, ORMModel):
    project_id: int


class MilestoneCreate(BaseModel):
    name: str = Field(min_length=1)
    planned_date: date
    actual_date: date | None = None
    status: str
    sequence_no: int = Field(ge=1)
    dependency_milestone_id: int | None = None


class MilestoneRead(MilestoneCreate, ORMModel):
    milestone_id: int
    project_id: int


class ProgressReportCreate(BaseModel):
    report_date: date
    physical_progress_pct: float = Field(ge=0, le=100)
    expenditure_cumulative: float = Field(ge=0)
    remarks: str | None = None


class ProgressReportRead(ProgressReportCreate, ORMModel):
    report_id: int
    project_id: int


class RiskScoreRead(ORMModel):
    score_id: int
    project_id: int
    computed_at: datetime
    health_score: float = Field(ge=0, le=100)
    delay_probability: float = Field(ge=0, le=1)
    cost_overrun_estimate: float
    component_breakdown: dict[str, Any]


class AlertCreate(BaseModel):
    alert_type: str
    severity: str
    explanation_text: str = Field(min_length=1)
    status: str = "OPEN"


class AlertRead(AlertCreate, ORMModel):
    alert_id: int
    project_id: int
    generated_at: datetime
