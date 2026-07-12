import json
import pytest
import uuid
from unittest.mock import MagicMock
from app.recognition.pipeline import PipelineError
from app.recognition.quality.base import QualityCode, QualityResult

@pytest.mark.asyncio
async def test_not_found_error_format(test_client):
    resp = await test_client.get(f"/api/v1/candidates/{uuid.uuid4()}")
    assert resp.status_code == 404
    body = resp.json()
    assert "error" in body
    assert body["error"]["code"] == "not_found"
    assert "message" in body["error"]
    assert "details" in body["error"]


@pytest.mark.asyncio
async def test_conflict_error_format(test_client):
    # First creation
    await test_client.post("/api/v1/candidates/", json={
        "candidate_id": "TEST_ERR_001",
        "name": "Test Conflict",
        "email": "conflict@example.com",
    })
    # Duplicate creation
    resp = await test_client.post("/api/v1/candidates/", json={
        "candidate_id": "TEST_ERR_001",
        "name": "Test Conflict",
        "email": "conflict2@example.com",
    })
    assert resp.status_code == 409
    body = resp.json()
    assert "error" in body
    assert body["error"]["code"] == "conflict"
    assert "message" in body["error"]


@pytest.mark.asyncio
async def test_validation_error_format(test_client):
    # Missing candidate_id, invalid email
    resp = await test_client.post("/api/v1/candidates/", json={
        "name": "Test Valid",
        "email": "not_an_email",
    })
    assert resp.status_code == 422
    body = resp.json()
    assert "error" in body
    assert body["error"]["code"] == "validation_error"
    assert "message" in body["error"]
    assert "details" in body["error"]


@pytest.mark.asyncio
async def test_quality_check_error_format(test_client, mock_pipeline):
    # Make mock pipeline return a quality check failure
    quality_fail = QualityResult(passed=False, code=QualityCode.BLURRY, message="Image is blurry")
    mock_pipeline.process.return_value = PipelineError(
        quality=quality_fail,
        message="Quality check failed: image is blurry"
    )

    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), color=(128, 128, 128)).save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    resp = await test_client.post(
        "/api/v1/face/upload",
        data={
            "candidate_id": "CAM_FAIL_001",
            "name": "Fail Quality",
            "email": "fail@example.com",
        },
        files={"image": ("face.jpg", img_bytes, "image/jpeg")},
    )
    assert resp.status_code == 422
    body = resp.json()
    assert "error" in body
    assert body["error"]["code"] == "quality_check_failed"
    assert "quality_code" in body["error"]["details"]
    assert body["error"]["details"]["quality_code"] == "blurry"


@pytest.mark.asyncio
async def test_route_not_found_format(test_client):
    resp = await test_client.get("/api/v1/nonexistent_route_abc123")
    assert resp.status_code == 404
    body = resp.json()
    assert "error" in body
    assert body["error"]["code"] == "not_found"
    assert "message" in body["error"]
    assert "details" in body["error"]


@pytest.mark.asyncio
async def test_method_not_allowed_format(test_client):
    resp = await test_client.post("/api/v1/health")
    assert resp.status_code == 405
    body = resp.json()
    assert "error" in body
    assert body["error"]["code"] == "method_not_allowed"
    assert "message" in body["error"]
    assert "details" in body["error"]


def test_rate_limit_handler_format():
    from app.middleware.rate_limiter import rate_limit_exceeded_handler

    response = rate_limit_exceeded_handler(None, Exception("limit exceeded"))
    assert response.status_code == 429
    body = json.loads(response.body.decode())
    assert "error" in body
    assert body["error"]["code"] == "rate_limit_exceeded"
    assert "message" in body["error"]
    assert "details" in body["error"]
