"""
Input sanitization utilities.

SQLAlchemy ORM parameterizes all queries automatically, so these helpers
provide extra defense-in-depth for string fields stored verbatim.
"""
import re


# Characters that have no business in a candidate_id or name
_DANGEROUS_CHARS = re.compile(r"[<>\"'%;()&+]")
_MAX_SAFE_STRING = 500


def sanitize_string(value: str, max_length: int = _MAX_SAFE_STRING) -> str:
    """
    Strip dangerous characters and truncate to max_length.
    Raises ValueError if the sanitized result is empty.
    """
    cleaned = _DANGEROUS_CHARS.sub("", value).strip()
    if not cleaned:
        raise ValueError(f"Input sanitized to empty string: {value!r}")
    return cleaned[:max_length]


def is_safe_filename(filename: str) -> bool:
    """Return True if the filename contains no path traversal characters."""
    dangerous = {"../", "..\\", "/", "\\", "\x00"}
    return not any(d in filename for d in dangerous)
