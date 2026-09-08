from datetime import date
from decimal import Decimal

import joblib
import pandas as pd

from app.config import settings


FEATURE_COLUMNS = [
    "Sector Name",
    "Line Ministry",
    "Implementing Agency",
    "Original Cost (in cr.)",
    "Expenditure (in cr.)",
    "Physical Progress (in %)",
    "Planned Duration (days)",
    "Expenditure Ratio (%)",
    "Expenditure-Progress Gap (%)",
    "Cost Base Anomaly",
]

cost_model = joblib.load(settings.cost_model_path)
delay_model = joblib.load(settings.delay_model_path)


def _number(value: Decimal | int | float | None) -> float:
    return float(value or 0)


def build_features(project, progress) -> pd.DataFrame:
    original_cost = _number(project.sanctioned_cost)
    cost_base = _number(project.revised_cost or project.sanctioned_cost)
    expenditure = _number(progress.expenditure_cumulative if progress else 0)
    physical_progress = _number(progress.physical_progress_pct if progress else 0)
    duration = (project.planned_end_date - project.start_date).days
    expenditure_ratio = (expenditure / cost_base * 100) if cost_base else 0

    return pd.DataFrame([{
        "Sector Name": project.sector,
        "Line Ministry": project.ministry,
        "Implementing Agency": project.implementing_agency,
        "Original Cost (in cr.)": original_cost,
        "Expenditure (in cr.)": expenditure,
        "Physical Progress (in %)": physical_progress,
        "Planned Duration (days)": duration,
        "Expenditure Ratio (%)": expenditure_ratio,
        "Expenditure-Progress Gap (%)": expenditure_ratio - physical_progress,
        "Cost Base Anomaly": int(cost_base > 0 and expenditure > 10 * cost_base),
    }], columns=FEATURE_COLUMNS)


def predict(project, progress) -> dict[str, float]:
    features = build_features(project, progress)
    return {
        "cost_overrun_probability": float(cost_model.predict_proba(features)[0][1]),
        "delay_probability": float(delay_model.predict_proba(features)[0][1]),
    }
