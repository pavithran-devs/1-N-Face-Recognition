"""
Face Enrollment Service — FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload
"""
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.router import api_router
from app.config.settings import get_settings
from app.core.events import lifespan
from app.exceptions import AppError
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limiter import limiter, rate_limit_exceeded_handler

settings = get_settings()

# ── Logging configuration ──────────────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
    colorize=True,
)
logger.add(
    "enrollment_service.log",
    rotation="10 MB",
    retention="1 week",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} — {message}",
    colorize=False,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Face Enrollment Service",
        description=(
            "Production-grade face enrollment API. "
            "Registers candidates, generates ArcFace embeddings, and exports data for identification."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── Rate limiter ──────────────────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # ── Request logging ───────────────────────────────────────────────────────
    app.add_middleware(LoggingMiddleware)

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom exception handler ──────────────────────────────────────────────
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning("AppError {}: {}", exc.error_code, exc.message)
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    from fastapi.exceptions import RequestValidationError

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("Validation error: {}", exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Validation failed.",
                    "details": {
                        "errors": exc.errors()
                    }
                }
            },
        )

    from starlette.exceptions import HTTPException as StarletteHTTPException

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        logger.warning("HTTPException {}: {}", exc.status_code, exc.detail)
        if exc.status_code == 404:
            code = "not_found"
        elif exc.status_code == 405:
            code = "method_not_allowed"
        else:
            code = "http_error"
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": code,
                    "message": str(exc.detail),
                    "details": {},
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error: {}", exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred.",
                    "details": {},
                }
            },
        )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_router)

    return app


app = create_app()
