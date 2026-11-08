"""
Application settings and configuration management via Pydantic Settings.
"""

from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base Directory Resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Centralized configuration parameters for the system."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application & Environment
    PROJECT_NAME: str = "Advanced QR Code Payment Fraud Detection System"
    VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    SECRET_KEY: str = Field(default="dev_insecure_secret_key_change_in_production")
    PII_SECRET_SALT: str = Field(default="dev_default_salt_2026_qr_fraud")

    # Database Settings
    DATABASE_URL: str = Field(default=f"sqlite:///{PROJECT_ROOT / 'database' / 'fraud_detection.db'}")
    SQL_ECHO: bool = False

    # Caching Strategy
    CACHE_BACKEND: Literal["memory", "redis"] = "memory"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Model Parameters & Gating Weights
    WEIGHT_SUPERVISED: float = 0.70
    WEIGHT_ANOMALY: float = 0.30
    THRESHOLD_APPROVE: float = 0.30
    THRESHOLD_BLOCK: float = 0.70
    ZERO_DAY_ANOMALY_ESCALATION: float = 0.80

    # Latency & Watchdog
    TIMEOUT_CIRCUIT_BREAKER_MS: int = 120
    SELECTIVE_SHAP_OPTIMIZATION: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = Field(default=str(PROJECT_ROOT / "logs" / "application.log"))


# Singleton Settings Instance
settings = Settings()

