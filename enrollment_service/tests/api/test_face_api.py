"""API tests for /api/v1/face enrollment endpoints."""
import base64
import io

import pytest
from PIL import Image


def _make_jpeg_b64() -> str:
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), color=(128, 128, 128)).save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()


def _make_jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), color=(128, 128, 128)).save(buf, format="JPEG")
    return buf.getvalue()


class TestFaceAPI:
    @pytest.mark.asyncio
    async def test_upload_face_creates_candidate(self, test_client):
        img_bytes = _make_jpeg_bytes()
        resp = await test_client.post(
            "/api/v1/face/upload",
            data={
                "candidate_id": "CAM001",
                "name": "Frank",
                "email": "frank@example.com",
            },
            files={"image": ("face.jpg", img_bytes, "image/jpeg")},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert "candidate" in body
        assert "embedding" in body
        assert body["candidate"]["candidate_id"] == "CAM001"

    @pytest.mark.asyncio
    async def test_capture_face_creates_candidate(self, test_client):
        resp = await test_client.post(
            "/api/v1/face/capture",
            json={
                "image_b64": _make_jpeg_b64(),
                "candidate_id": "CAM002",
                "name": "Grace",
                "email": "grace@example.com",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["candidate"]["candidate_id"] == "CAM002"
        assert body["embedding"]["embedding_dimension"] == 512

    @pytest.mark.asyncio
    async def test_duplicate_enrollment_returns_409(self, test_client):
        img_bytes = _make_jpeg_bytes()
        await test_client.post(
            "/api/v1/face/upload",
            data={"candidate_id": "CAM003", "name": "Heidi", "email": "heidi@example.com"},
            files={"image": ("face.jpg", img_bytes, "image/jpeg")},
        )
        resp = await test_client.post(
            "/api/v1/face/upload",
            data={"candidate_id": "CAM003", "name": "Heidi", "email": "heidi2@example.com"},
            files={"image": ("face.jpg", img_bytes, "image/jpeg")},
        )
        assert resp.status_code == 409
