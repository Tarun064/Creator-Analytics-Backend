"""
Application configuration from environment variables.
Loads .env from backend/ when running without Docker.
"""
import os
from pathlib import Path
from typing import List

# Load .env from backend directory when present (for local run without Docker)
_env_file = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_file)


class Settings:
    """App settings loaded from env."""

    # App
    APP_NAME: str = "AI Creator Analytics"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database: default SQLite (no setup – file created in backend/). Set DATABASE_URL for PostgreSQL.
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./creator_analytics.db",
    )

    # Redis (optional when running without Docker; use localhost if Redis is local)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS (for production set CORS_ORIGINS to comma-separated URLs, e.g. your Vercel URL)
    CORS_ORIGINS: List[str] = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")]

    # Celery (use localhost when running without Docker)
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")


settings = Settings()
