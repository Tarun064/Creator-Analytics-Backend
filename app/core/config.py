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

    # Database
    _db_url = os.getenv("DATABASE_URL")
    if _db_url:
        # Fix for SQLAlchemy asyncpg: it needs postgresql+asyncpg://
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif _db_url.startswith("postgresql://"):
            _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    DATABASE_URL: str = _db_url or (
        "sqlite+aiosqlite:///./creator_analytics.db" if not os.getenv("VERCEL") else "sqlite+aiosqlite:////tmp/creator_analytics.db"
    )

    # Redis (optional when running without Docker; use localhost if Redis is local)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    # If CORS_ORIGINS is set, split it. Otherwise allow all ("*") for easier initial setup/debugging.
    _cors_env = os.getenv("CORS_ORIGINS")
    CORS_ORIGINS: List[str] = [x.strip() for x in _cors_env.split(",")] if _cors_env else ["*"]

    # Celery (use localhost when running without Docker)
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")


settings = Settings()
