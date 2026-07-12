"""Health check endpoint."""
from fastapi import APIRouter, Request

from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Service health check")
async def health(request: Request) -> HealthResponse:
    pipeline = getattr(request.app.state, "pipeline", None)
    pipeline_loaded = pipeline is not None and pipeline.is_loaded
    return HealthResponse(
        status="ok",
        version="1.0.0",
        pipeline_loaded=pipeline_loaded,
    )
