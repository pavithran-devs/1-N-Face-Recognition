"""Logging configuration using Loguru."""

import logging
import sys

from loguru import logger

from app.config.settings import get_settings


class InterceptHandler(logging.Handler):
    """
    Default handler from python logging to loguru.
    See: https://loguru.readthedocs.io/en/stable/resources/recipes.html#reconnecting-standard-logging-to-loguru
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    """Configures application-wide logging with Loguru."""
    settings = get_settings()
    log_level = settings.log_level.upper()

    # Remove all default handlers
    logger.remove()

    # Add console logger
    logger.add(
        sys.stdout,
        enqueue=True,
        backtrace=True,
        diagnose=True,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )

    # Add file logger
    logger.add(
        "face_identification.log",
        rotation="10 MB",
        retention="1 week",
        enqueue=True,
        backtrace=True,
        diagnose=True,
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} - "
            "{message}"
        ),
        colorize=False,
    )

    # Route standard logging logs to Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Adjust levels for noisy third-party loggers
    for logger_name in ("uvicorn.access", "uvicorn.error", "sqlalchemy.engine", "asyncio"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    logger.info("Logging configured successfully. Level: {}", log_level)
