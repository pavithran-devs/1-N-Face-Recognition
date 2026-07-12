"""
Rate limiting setup using slowapi (Starlette-compatible wrapper for limits).

Usage in main.py:
    from app.middleware.rate_limiter import limiter, rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
"""
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
