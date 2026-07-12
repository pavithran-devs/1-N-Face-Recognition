"""Image file validation: MIME type, size, decodability."""
import io

from PIL import Image, UnidentifiedImageError

from app.config.settings import get_settings
from app.exceptions import ImageValidationError

_settings = get_settings()
_MAX_BYTES = _settings.max_image_size_mb * 1024 * 1024
_ALLOWED_FORMATS = {"JPEG", "PNG", "BMP"}


def validate_image_bytes(data: bytes, *, filename: str = "image") -> None:
    """
    Raise ImageValidationError if the image data fails any check.

    Checks:
      - File size ≤ max_image_size_mb
      - Format is JPEG, PNG, or BMP
      - Decodable as a real image
    """
    if len(data) > _MAX_BYTES:
        raise ImageValidationError(
            f"{filename}: file size {len(data) // 1024}KB exceeds "
            f"maximum {_settings.max_image_size_mb}MB."
        )

    try:
        img = Image.open(io.BytesIO(data))
        img.verify()  # Check file integrity without fully decoding
    except (UnidentifiedImageError, Exception) as exc:
        raise ImageValidationError(
            f"{filename}: could not decode image — {exc}"
        ) from exc

    # Re-open after verify (verify() closes the file)
    img = Image.open(io.BytesIO(data))
    if img.format not in _ALLOWED_FORMATS:
        raise ImageValidationError(
            f"{filename}: unsupported format '{img.format}'. "
            f"Allowed: {', '.join(_ALLOWED_FORMATS)}."
        )
