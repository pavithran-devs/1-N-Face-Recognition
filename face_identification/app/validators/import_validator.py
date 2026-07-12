"""Validation logic for imported candidate records."""

from app.config.settings import get_settings

_settings = get_settings()
_REQUIRED_FIELDS = {"candidate_id", "name", "email"}


def validate_import_record(record: dict) -> None:
    """
    Raise ValueError if a record is missing required fields or has invalid data.
    """
    missing = _REQUIRED_FIELDS - set(record.keys())
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    if not record["candidate_id"].strip():
        raise ValueError("candidate_id must not be blank.")
    if not record["name"].strip():
        raise ValueError("name must not be blank.")
    if "@" not in record["email"]:
        raise ValueError(f"Invalid email: {record['email']!r}")

    embeddings = record.get("embeddings", [])
    for emb in embeddings:
        embedding = emb.get("embedding", [])
        if isinstance(embedding, str):
            # Parse CSV format (semicolon-separated float string)
            try:
                parts = [float(x) for x in embedding.split(";") if x.strip()]
                embedding = parts
            except Exception as exc:
                raise ValueError(f"Failed to parse CSV embedding: {exc}") from exc

        if len(embedding) != _settings.embedding_dimension:
            raise ValueError(
                f"Embedding dimension mismatch: got {len(embedding)}, "
                f"expected {_settings.embedding_dimension}."
            )
