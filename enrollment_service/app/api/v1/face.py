"""Face enrollment endpoints: file upload and webcam capture."""
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import get_enrollment_service
from app.schemas.candidate import CandidateCreate, CandidateResponse
from app.schemas.face import EnrollmentResponse, FaceCaptureRequest
from app.schemas.face_embedding import EmbeddingResponse
from app.services.enrollment import EnrollmentService

router = APIRouter(prefix="/face", tags=["Face Enrollment"])


@router.post("/upload", response_model=EnrollmentResponse, status_code=201)
async def upload_face(
    service: Annotated[EnrollmentService, Depends(get_enrollment_service)],
    image: UploadFile = File(..., description="Face image file (JPEG/PNG/BMP)"),
    candidate_id: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    dob: str | None = Form(None),
) -> EnrollmentResponse:
    """
    Enroll a new candidate via file upload.
    All candidate fields are provided as form data alongside the image.
    """
    from datetime import date

    dob_parsed = date.fromisoformat(dob) if dob else None
    candidate_data = CandidateCreate(
        candidate_id=candidate_id,
        name=name,
        email=email,
        dob=dob_parsed,
    )

    image_bytes = await image.read()
    result = await service.enroll_from_bytes(image_bytes, candidate_data)

    return EnrollmentResponse(
        candidate=CandidateResponse.model_validate(result.candidate),
        embedding=EmbeddingResponse.model_validate(result.embedding),
        quality_code=result.quality_code,
        timings=result.timings,
    )


@router.post("/capture", response_model=EnrollmentResponse, status_code=201)
async def capture_face(
    data: FaceCaptureRequest,
    service: Annotated[EnrollmentService, Depends(get_enrollment_service)],
) -> EnrollmentResponse:
    """
    Enroll a new candidate via base64-encoded webcam capture.
    The image_b64 field should contain the full base64 string (with or without data URI prefix).
    """
    candidate_data = CandidateCreate(
        candidate_id=data.candidate_id,
        name=data.name,
        email=data.email,
        dob=data.dob,
    )
    result = await service.enroll_from_base64(data.image_b64, candidate_data)
    return EnrollmentResponse(
        candidate=CandidateResponse.model_validate(result.candidate),
        embedding=EmbeddingResponse.model_validate(result.embedding),
        quality_code=result.quality_code,
        timings=result.timings,
    )
