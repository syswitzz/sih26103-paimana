"""Small, dependency-free application configuration layer."""
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
import os


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_DIR = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")

def _path(name: str, default: str) -> Path:
    value = Path(os.getenv(name, default))
    return value if value.is_absolute() else (BACKEND_DIR / value).resolve()


@dataclass(frozen=True)
class Settings:
    database_url: str
    cors_origins: list[str]
    environment: str
    dataset_path: Path
    cost_model_path: Path
    delay_model_path: Path
    model_version: str


def get_settings() -> Settings:
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return Settings(
        database_url=os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:paimana123@localhost:5432/paimana"),
        cors_origins=[origin.strip() for origin in origins.split(",") if origin.strip()],
        environment=os.getenv("ENVIRONMENT", "development"),
        dataset_path=_path("PROJECT_DATASET_PATH", "../ml/data/Projects_Report.csv"),
        cost_model_path=_path("ML_COST_MODEL_PATH", "../ml/models/cost_model.pkl"),
        delay_model_path=_path("ML_DELAY_MODEL_PATH", "../ml/models/delay_model.pkl"),
        model_version=os.getenv("ML_MODEL_VERSION", "sih-rf-v1"),
    )


settings = get_settings()
