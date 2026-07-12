"""API endpoint for application performance telemetry metrics."""

from fastapi import APIRouter

from app.core.telemetry import TelemetryTracker

router = APIRouter(tags=["metrics"])
telemetry = TelemetryTracker()


@router.get("/metrics")
async def metrics_endpoint() -> dict:
    """Returns real-time processing statistics, matching target requirements."""
    return telemetry.get_metrics()
