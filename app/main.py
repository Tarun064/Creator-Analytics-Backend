"""
AI Creator Analytics Dashboard - FastAPI Backend
Entry point and app configuration.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app import models  # noqa: F401 - register models with Base
from app.routers import auth, user, youtube, analytics, ai_suggestions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables and seed dummy data if empty."""
    try:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database ready.")
    except Exception as e:
        logger.error("Database initialization failed: %s", e)
    # Seed demo user + channel + videos + AI insights when DB is empty
    try:
        from app.services.seed_data import seed_if_empty
        await seed_if_empty()
    except Exception as e:
        logger.warning("Seed skipped or failed: %s", e)
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="AI Creator Analytics API",
    description="Backend API for creator analytics and AI insights",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(youtube.router, prefix="/youtube", tags=["youtube"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(ai_suggestions.router, prefix="/ai", tags=["ai"])


@app.get("/health")
async def health():
    """Health check for Docker/load balancers."""
    return {"status": "ok"}
