"""Application lifecycle events: startup model loading, shutdown cleanup."""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from loguru import logger

from app.config.settings import get_settings
from app.recognition.pipeline import FaceRecognitionPipeline


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown."""
    settings = get_settings()
    logger.info("Starting Face Enrollment Service v1.0.0")

    # Create exports directory if missing
    settings.export_dir.mkdir(parents=True, exist_ok=True)

    # Load the recognition pipeline (downloads models on first run)
    pipeline = FaceRecognitionPipeline()
    try:
        pipeline.load()
    except Exception as exc:
        logger.error("Pipeline failed to load: {}. Continuing without it.", exc)

    app.state.pipeline = pipeline

    logger.info("Startup complete — API ready.")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Shutting down Face Enrollment Service.")
