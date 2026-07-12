"""Unit tests for the Candidate Import Validator."""

import pytest

from app.validators.import_validator import validate_import_record


def test_validate_record_success() -> None:
    record = {
        "candidate_id": "CAND001",
        "name": "Jane Doe",
        "email": "jane@doe.com",
        "embeddings": [
            {
                "embedding": [0.5] * 512,
                "embedding_dimension": 512,
            }
        ],
    }
    # Should not raise any error
    validate_import_record(record)


def test_validate_record_missing_fields() -> None:
    # Missing email
    record = {
        "candidate_id": "CAND001",
        "name": "Jane Doe",
    }
    with pytest.raises(ValueError, match="Missing required fields"):
        validate_import_record(record)


def test_validate_record_blank_candidate_id() -> None:
    record = {
        "candidate_id": "   ",
        "name": "Jane Doe",
        "email": "jane@doe.com",
    }
    with pytest.raises(ValueError, match="candidate_id must not be blank"):
        validate_import_record(record)


def test_validate_record_blank_name() -> None:
    record = {
        "candidate_id": "CAND001",
        "name": "   ",
        "email": "jane@doe.com",
    }
    with pytest.raises(ValueError, match="name must not be blank"):
        validate_import_record(record)


def test_validate_record_invalid_email() -> None:
    record = {
        "candidate_id": "CAND001",
        "name": "Jane Doe",
        "email": "janedoe.com",  # Missing @
    }
    with pytest.raises(ValueError, match="Invalid email"):
        validate_import_record(record)


def test_validate_record_invalid_embedding_dimension() -> None:
    record = {
        "candidate_id": "CAND001",
        "name": "Jane Doe",
        "email": "jane@doe.com",
        "embeddings": [
            {
                "embedding": [0.5] * 256,  # 256 instead of 512
                "embedding_dimension": 256,
            }
        ],
    }
    with pytest.raises(ValueError, match="Embedding dimension mismatch"):
        validate_import_record(record)
