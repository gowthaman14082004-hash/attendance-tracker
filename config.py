"""
config.py — Application configuration.

Loads settings from environment variables (.env) so that no secrets
are ever committed to version control.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Pagination
    RECORDS_PER_PAGE: int = 20


class DevelopmentConfig(Config):
    """Local development settings."""

    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = (
        os.environ.get("DATABASE_URL") or "sqlite:///attendance.db"
    )
    SQLALCHEMY_ECHO: bool = False  # set True to log SQL queries


class ProductionConfig(Config):
    """Production settings — served via Gunicorn."""

    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = (
        os.environ.get("DATABASE_URL") or "sqlite:///attendance.db"
    )


# Map names → config classes for easy selection
config_map: dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
