"""Risk score computation shared by the API and the importer."""
from app.models.models import ProgressReport, RiskScore
from app.services.ml import predict


def build_risk_score(project, progress: ProgressReport | None) -> RiskScore:
    probabilities = predict(project, progress)
    cost_probability = probabilities["cost_overrun_probability"]
    delay_probability = probabilities["delay_probability"]
    risk_score = (cost_probability + delay_probability) * 50
    risk_level = "HIGH" if risk_score >= 67 else "MEDIUM" if risk_score >= 34 else "LOW"
    return RiskScore(
        project_id=project.project_id,
        health_score=max(0, 100 - risk_score),
        risk_score=risk_score,
        risk_level=risk_level,
        delay_probability=delay_probability,
        cost_overrun_probability=cost_probability,
        cost_overrun_estimate=max(0, cost_probability - 0.5) * float(project.revised_cost or project.sanctioned_cost),
        component_breakdown={"delay": delay_probability, "cost_overrun": cost_probability},
        model_version="sih-rf-v1",
    )
