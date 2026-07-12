"""Custom application exceptions."""


class AppError(Exception):
    """Base class for all application errors."""

    http_status: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(AppError):
    http_status = 404
    error_code = "not_found"


class ConflictError(AppError):
    http_status = 409
    error_code = "conflict"


class ValidationError(AppError):
    http_status = 422
    error_code = "validation_error"


class ImageValidationError(AppError):
    http_status = 422
    error_code = "image_validation_error"


class QualityCheckError(AppError):
    http_status = 422
    error_code = "quality_check_failed"

    def __init__(self, message: str, quality_code: str, details: dict | None = None) -> None:
        super().__init__(message, details)
        self.quality_code = quality_code
        self.details = self.details or {}
        self.details["quality_code"] = quality_code


class PipelineError(AppError):
    http_status = 500
    error_code = "pipeline_error"


class ImportError(AppError):
    http_status = 422
    error_code = "import_error"
