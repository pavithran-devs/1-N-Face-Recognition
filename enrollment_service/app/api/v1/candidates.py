"""Candidate CRUD endpoints."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_candidate_service
from app.schemas.candidate import (
    CandidateCreate,
    CandidateListResponse,
    CandidateResponse,
    CandidateUpdate,
)
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.services.candidate import CandidateService

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.post("/", response_model=CandidateResponse, status_code=201)
async def create_candidate(
    data: CandidateCreate,
    service: Annotated[CandidateService, Depends(get_candidate_service)],
) -> CandidateResponse:
    """Create a new candidate (without face enrollment)."""
    candidate = await service.create(data)
    return CandidateResponse.model_validate(candidate)


@router.get("/", response_model=PaginatedResponse[CandidateListResponse])
async def list_candidates(
    service: Annotated[CandidateService, Depends(get_candidate_service)],
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str | None = Query(None, description="Search term (matches name/candidate_id)"),
    search_field: str = Query("name", pattern="^(name|candidate_id)$"),
) -> PaginatedResponse[CandidateListResponse]:
    """List all candidates with optional search and pagination."""
    if search:
        items, meta = await service.search(search, field=search_field, offset=offset, limit=limit)
    else:
        items, meta = await service.list_all(offset=offset, limit=limit)
    return PaginatedResponse(
        data=[CandidateListResponse.model_validate(c) for c in items],
        pagination=meta,
    )


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: uuid.UUID,
    service: Annotated[CandidateService, Depends(get_candidate_service)],
) -> CandidateResponse:
    """Retrieve a single candidate by UUID."""
    candidate = await service.get_by_id(candidate_id)
    return CandidateResponse.model_validate(candidate)


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: uuid.UUID,
    data: CandidateUpdate,
    service: Annotated[CandidateService, Depends(get_candidate_service)],
) -> CandidateResponse:
    """Update an existing candidate's metadata."""
    candidate = await service.update(candidate_id, data)
    return CandidateResponse.model_validate(candidate)


@router.delete("/{candidate_id}", status_code=204)
async def delete_candidate(
    candidate_id: uuid.UUID,
    service: Annotated[CandidateService, Depends(get_candidate_service)],
) -> None:
    """Delete a candidate and all associated embeddings."""
    await service.delete(candidate_id)
