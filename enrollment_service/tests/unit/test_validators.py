"""Unit tests for image and import validators."""
import io

import pytest
from PIL import Image

from app.exceptions import ImageValidationError
from app.validators.image import validate_image_bytes
from app.validators.import_validator import validate_import_record


# ── Image validator ───────────────────────────────────────────────────────────

def _make_jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), color=(200, 100, 50)).save(buf, format="JPEG")
    return buf.getvalue()


def _make_png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (100, 100)).save(buf, format="PNG")
    return buf.getvalue()


class TestImageValidator:
    def test_valid_jpeg(self):
        validate_image_bytes(_make_jpeg_bytes())  # no exception

    def test_valid_png(self):
        validate_image_bytes(_make_png_bytes())

    def test_invalid_data(self):
        with pytest.raises(ImageValidationError):
            validate_image_bytes(b"not-an-image")

    def test_oversized(self):
        # Build data larger than 10MB
        huge = b"\xff\xd8\xff" + b"x" * (11 * 1024 * 1024)
        with pytest.raises(ImageValidationError, match="exceeds maximum"):
            validate_image_bytes(huge)


# ── Import validator ──────────────────────────────────────────────────────────

def _good_record() -> dict:
    return {
        "candidate_id": "EMP001",
        "name": "Alice",
        "email": "alice@example.com",
        "embeddings": [{"embedding": [0.1] * 512}],
    }


class TestImportValidator:
    def test_valid_record(self):
        validate_import_record(_good_record())  # no exception

    def test_missing_candidate_id(self):
        r = _good_record()
        del r["candidate_id"]
        with pytest.raises(ValueError, match="Missing required fields"):
            validate_import_record(r)

    def test_missing_email(self):
        r = _good_record()
        del r["email"]
        with pytest.raises(ValueError):
            validate_import_record(r)

    def test_invalid_email(self):
        r = _good_record()
        r["email"] = "not-an-email"
        with pytest.raises(ValueError, match="Invalid email"):
            validate_import_record(r)

    def test_wrong_embedding_dimension(self):
        r = _good_record()
        r["embeddings"] = [{"embedding": [0.1] * 128}]  # wrong dim
        with pytest.raises(ValueError, match="Embedding dimension mismatch"):
            validate_import_record(r)

    def test_no_embeddings_ok(self):
        r = _good_record()
        r["embeddings"] = []
        validate_import_record(r)  # no exception
