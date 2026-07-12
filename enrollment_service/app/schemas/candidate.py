"""Pydantic schemas for the Candidate resource."""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class CandidateCreate(BaseModel):
    candidate_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    dob: date | None = None


class CandidateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    dob: date | None = None


class CandidateResponse(BaseModel):
    id: uuid.UUID
    candidate_id: str
    name: str
    email: str
    dob: date | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CandidateListResponse(BaseModel):
    id: uuid.UUID
    candidate_id: str
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
