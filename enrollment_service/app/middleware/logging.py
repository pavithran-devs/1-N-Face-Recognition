"""Request/response logging middleware using Loguru."""
import time
import uuid

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every request with:
      - A unique request_id
      - Method, path, status code
      - Processing time in ms
    """

    async def dispatch(self, request: Request, call_next: object) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        logger.info(
            "[{}] → {} {}",
            request_id,
            request.method,
            request.url.path,
        )

        response: Response = await call_next(request)  # type: ignore[operator]
        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "[{}] ← {} {} ({:.1f}ms)",
            request_id,
            response.status_code,
            request.url.path,
            elapsed_ms,
        )

        # Pass the request_id back to the client for correlation
        response.headers["X-Request-ID"] = request_id
        return response
