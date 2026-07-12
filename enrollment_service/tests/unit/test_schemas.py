"""Unit tests for Pydantic schemas."""
import uuid
from datetime import date, datetime

import pytest

from app.schemas.candidate import CandidateCreate, CandidateUpdate
from app.schemas.common import PaginationMeta
from app.schemas.face import FaceCaptureRequest


class TestCandidateCreate:
    def test_valid(self):
        c = CandidateCreate(
            candidate_id="EMP001",
            name="Alice Smith",
            email="alice@example.com",
        )
        assert c.candidate_id == "EMP001"
        assert c.dob is None

    def test_with_dob(self):
        c = CandidateCreate(
            candidate_id="EMP002",
            name="Bob",
            email="bob@example.com",
            dob=date(1990, 5, 20),
        )
        assert c.dob == date(1990, 5, 20)

    def test_invalid_email(self):
        with pytest.raises(Exception):
            CandidateCreate(candidate_id="x", name="x", email="not-an-email")

    def test_blank_candidate_id(self):
        with pytest.raises(Exception):
            CandidateCreate(candidate_id="", name="x", email="x@x.com")


class TestCandidateUpdate:
    def test_all_optional(self):
        u = CandidateUpdate()
        assert u.name is None
        assert u.email is None

    def test_partial(self):
        u = CandidateUpdate(name="New Name")
        assert u.name == "New Name"
        assert u.email is None


class TestPaginationMeta:
    def test_has_next(self):
        m = PaginationMeta(total=50, offset=0, limit=10, has_next=True, has_prev=False)
        assert m.has_next is True
        assert m.has_prev is False


class TestFaceCaptureRequest:
    def test_valid(self):
        r = FaceCaptureRequest(
            image_b64="abc123==",
            candidate_id="EMP001",
            name="Alice",
            email="alice@example.com",
        )
        assert r.image_b64 == "abc123=="
