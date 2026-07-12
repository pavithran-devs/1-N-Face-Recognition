"""Schemas for face upload and capture requests."""
import uuid
from datetime import date

from pydantic import BaseModel, EmailStr, Field

from app.schemas.candidate import CandidateResponse
from app.schemas.face_embedding import EmbeddingResponse


class FaceCaptureRequest(BaseModel):
    """Payload for base64 webcam capture enrollment."""
    image_b64: str = Field(..., description="Base64-encoded image (JPEG/PNG/BMP).")
    candidate_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    dob: date | None = None


class EnrollmentResponse(BaseModel):
    """Returned after a successful enrollment."""
    candidate: CandidateResponse
    embedding: EmbeddingResponse
    quality_code: str
    timings: dict[str, float]
