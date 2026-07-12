"""Rate limiting setup using slowapi."""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config.settings import get_settings

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
)


def rate_limit_exceeded_handler(request: Request, exc: Exception) -> Response:
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "rate_limit_exceeded",
                "message": "Too many requests. Please slow down.",
                "details": {},
            }
        },
    )
