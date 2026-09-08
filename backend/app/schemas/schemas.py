from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

class ProjectStatus(StrEnum):
    PLANNING="PLANNING"; IN_PROGRESS="IN_PROGRESS"; DELAYED="DELAYED"; COMPLETED="COMPLETED"; ON_HOLD="ON_HOLD"
class MilestoneStatus(StrEnum):
    PLANNED="PLANNED"; IN_PROGRESS="IN_PROGRESS"; COMPLETED="COMPLETED"; DELAYED="DELAYED"; CANCELLED="CANCELLED"
class AlertSeverity(StrEnum):
    CRITICAL="CRITICAL"; HIGH="HIGH"; MEDIUM="MEDIUM"; LOW="LOW"
class AlertStatus(StrEnum):
    OPEN="OPEN"; ACKNOWLEDGED="ACKNOWLEDGED"; RESOLVED="RESOLVED"; DISMISSED="DISMISSED"
class ORMModel(BaseModel):
    model_config=ConfigDict(from_attributes=True)
class ProjectCreate(BaseModel):
    name:str=Field(min_length=1,max_length=255); sector:str=Field(min_length=1,max_length=100); ministry:str=Field(min_length=1,max_length=150); implementing_agency:str=Field(min_length=1,max_length=200)
    state:str=Field(min_length=1,max_length=100); district:str=Field(min_length=1,max_length=100); sanctioned_cost:Decimal=Field(gt=0,max_digits=18,decimal_places=2); revised_cost:Decimal|None=Field(default=None,gt=0,max_digits=18,decimal_places=2)
    start_date:date; planned_end_date:date; current_status:ProjectStatus; category:str=Field(min_length=1,max_length=100)
    @model_validator(mode="after")
    def valid(self):
        if self.planned_end_date < self.start_date: raise ValueError("planned_end_date must be on or after start_date")
        if self.revised_cost is not None and self.revised_cost < self.sanctioned_cost: raise ValueError("revised_cost must be at least sanctioned_cost")
        return self
class ProjectRead(ProjectCreate,ORMModel): project_id:int; size_bucket:str
class LatestProgress(ORMModel): report_id:int; report_date:date; physical_progress_pct:Decimal; expenditure_cumulative:Decimal; remarks:str|None=None
class RiskScoreRead(ORMModel):
    score_id:int; project_id:int; computed_at:datetime; health_score:Decimal; risk_score:Decimal; risk_level:str; delay_probability:Decimal; cost_overrun_probability:Decimal; cost_overrun_estimate:Decimal; component_breakdown:dict[str,Any]; model_version:str
class ProjectDetailRead(ProjectRead): latest_progress:LatestProgress|None=None; latest_risk:RiskScoreRead|None=None
class ProjectListItem(ORMModel):
    project_id:int; name:str; ministry:str; sector:str; state:str; district:str; current_status:str; size_bucket:str; latest_risk:RiskScoreRead|None=None
class PaginatedProjects(BaseModel): items:list[ProjectListItem]; page:int; page_size:int; total:int
class MilestoneCreate(BaseModel):
    name:str=Field(min_length=1,max_length=255); planned_date:date; actual_date:date|None=None; status:MilestoneStatus; sequence_no:int=Field(ge=1); dependency_milestone_id:int|None=None
class MilestoneRead(MilestoneCreate,ORMModel): milestone_id:int; project_id:int
class ProgressReportCreate(BaseModel): report_date:date; physical_progress_pct:Decimal=Field(ge=0,le=100,max_digits=5,decimal_places=2); expenditure_cumulative:Decimal=Field(ge=0,max_digits=18,decimal_places=2); remarks:str|None=None
class ProgressReportRead(ProgressReportCreate,ORMModel): report_id:int; project_id:int
class AlertCreate(BaseModel): alert_type:str=Field(min_length=1,max_length=50); severity:AlertSeverity; explanation_text:str=Field(min_length=1); status:AlertStatus=AlertStatus.OPEN
class AlertRead(AlertCreate,ORMModel): alert_id:int; project_id:int; generated_at:datetime
class DashboardSummary(BaseModel): total_projects:int; total_sanctioned_cost:Decimal; total_revised_cost:Decimal; average_physical_progress:Decimal|None; status_distribution:dict[str,int]; risk_distribution:dict[str,int]; open_alerts:int
class StateRisk(BaseModel): state:str; project_count:int; average_risk_score:Decimal|None; risk_level:str|None
