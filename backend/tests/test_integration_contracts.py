from datetime import date
from types import SimpleNamespace

from app.main import app
from app.services.ml import build_features, predict


def test_expected_api_paths_are_exposed():
    paths = app.openapi()["paths"]
    assert "/api/projects" in paths
    assert "/api/projects/{project_id}" in paths
    assert "/api/dashboard/summary" in paths
    assert "/api/dashboard/state-risks" in paths
    assert "/api/projects/{project_id}/risk/predict" in paths


def test_existing_models_accept_database_fields():
    project = SimpleNamespace(
        sector="Roads",
        ministry="Ministry of Road Transport",
        implementing_agency="Implementation Unit",
        sanctioned_cost=1000,
        revised_cost=1100,
        start_date=date(2020, 1, 1),
        planned_end_date=date(2025, 1, 1),
    )
    progress = SimpleNamespace(expenditure_cumulative=500, physical_progress_pct=45)

    features = build_features(project, progress)
    probabilities = predict(project, progress)

    assert list(features.columns) == [
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
    assert 0 <= probabilities["cost_overrun_probability"] <= 1
    assert 0 <= probabilities["delay_probability"] <= 1
