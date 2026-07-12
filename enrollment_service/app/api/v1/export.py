"""Export endpoints: JSON and CSV."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_export_service
from app.schemas.export import ExportSummary
from app.services.export import ExportService

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/json", response_model=ExportSummary)
async def export_json(
    service: Annotated[ExportService, Depends(get_export_service)],
    candidate_id: uuid.UUID | None = Query(
        None, description="Export a single candidate by UUID; omit for all candidates."
    ),
) -> ExportSummary:
    """Export candidates (and their embeddings) as JSON."""
    if candidate_id:
        return await service.export_single_json(candidate_id)
    return await service.export_all_json()


@router.get("/csv", response_model=ExportSummary)
async def export_csv(
    service: Annotated[ExportService, Depends(get_export_service)],
    candidate_id: uuid.UUID | None = Query(
        None, description="Export a single candidate by UUID; omit for all candidates."
    ),
) -> ExportSummary:
    """Export candidates (and their embeddings) as CSV."""
    if candidate_id:
        return await service.export_single_csv(candidate_id)
    return await service.export_all_csv()
