"""
config.py
=========
Central configuration for the Smart Retry & Flaky Test Detection Framework.

All runtime-tunable values are sourced from environment variables (via a .env
file loaded with python-dotenv) with sane production-safe defaults. Nothing
here should be hardcoded deep inside the app -- other modules import from
this file so there is a single source of truth.
"""

from __future__ import annotations

import os
import secrets
from pathlib import Path
from dataclasses import dataclass, field

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _bool(value: str | None, default: bool = False) -> bool:
    """Parse a truthy/falsy string coming from the environment."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Config:
    """Base configuration shared by every environment."""

    # --- Flask core -----------------------------------------------------
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    DEBUG: bool = _bool(os.getenv("FLASK_DEBUG"), default=False)
    HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("FLASK_PORT", "5000"))

    # --- Paths ------------------------------------------------------------
    BASE_DIR: Path = BASE_DIR
    DATABASE_PATH: Path = BASE_DIR / "database" / "framework.db"
    # Legacy screenshots dir (kept for backward-compat); new code uses EVIDENCE_DIR
    SCREENSHOTS_DIR: Path = BASE_DIR / "evidence" / "screenshots"
    LOGS_DIR: Path = BASE_DIR / "logs"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    WEBSITE_PROFILES_DIR: Path = BASE_DIR / "website_profiles"
    EVIDENCE_DIR: Path = BASE_DIR / "evidence"

    # --- Selenium / test execution -----------------------------------------
    DEFAULT_BROWSER: str = os.getenv("DEFAULT_BROWSER", "chrome")  # chrome|edge|firefox
    HEADLESS: bool = _bool(os.getenv("HEADLESS"), default=False)
    IMPLICIT_WAIT: int = int(os.getenv("IMPLICIT_WAIT", "0"))
    EXECUTION_TIMEOUT: int = int(os.getenv("EXECUTION_TIMEOUT", "60"))  # seconds per test

    # --- Smart Retry Engine ------------------------------------------------
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "1"))
    RETRY_DELAY_SECONDS: float = float(os.getenv("RETRY_DELAY_SECONDS", "1.0"))
    RETRY_BACKOFF_MULTIPLIER: float = float(os.getenv("RETRY_BACKOFF_MULTIPLIER", "1.0"))  # reduced from 1.5

    # --- Flaky Detection -----------------------------------------------------
    FLAKY_WINDOW_SIZE: int = int(os.getenv("FLAKY_WINDOW_SIZE", "10"))  # last N runs considered
    FLAKY_THRESHOLD_PCT: float = float(os.getenv("FLAKY_THRESHOLD_PCT", "20.0"))

    # --- AI Integration (Gemini) ------------------------------------------
    AI_ENABLED: bool = _bool(os.getenv("AI_ENABLED"), default=True)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    AI_REQUEST_TIMEOUT: int = int(os.getenv("AI_REQUEST_TIMEOUT", "15"))

    # --- Auth ---------------------------------------------------------------
    SESSION_LIFETIME_DAYS: int = int(os.getenv("SESSION_LIFETIME_DAYS", "7"))
    REMEMBER_ME_DAYS: int = int(os.getenv("REMEMBER_ME_DAYS", "30"))

    # --- Reporting ------------------------------------------------------------
    COMPANY_NAME: str = os.getenv("COMPANY_NAME", "Smart QA Labs")
    REPORT_LOGO_TEXT: str = os.getenv("REPORT_LOGO_TEXT", "SmartRetry")

    def ensure_directories(self) -> None:
        """Create every directory this app depends on if it does not exist yet."""
        for path in (
            self.DATABASE_PATH.parent,
            self.EVIDENCE_DIR,
            self.SCREENSHOTS_DIR,
            self.LOGS_DIR,
            self.REPORTS_DIR,
            self.WEBSITE_PROFILES_DIR,
        ):
            path.mkdir(parents=True, exist_ok=True)


@dataclass
class DevelopmentConfig(Config):
    DEBUG: bool = True


@dataclass
class ProductionConfig(Config):
    DEBUG: bool = False


@dataclass
class TestingConfig(Config):
    DEBUG: bool = True
    DATABASE_PATH: Path = BASE_DIR / "database" / "framework_test.db"


def get_config() -> Config:
    """Factory that returns the correct config object based on FLASK_ENV."""
    env = os.getenv("FLASK_ENV", "development").lower()
    mapping = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    cfg = mapping.get(env, DevelopmentConfig)()
    cfg.ensure_directories()
    return cfg


settings = get_config()
