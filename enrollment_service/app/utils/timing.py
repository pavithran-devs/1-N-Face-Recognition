"""Performance timing decorator."""
import functools
from time import perf_counter
from typing import Any, Callable, TypeVar

from loguru import logger

F = TypeVar("F", bound=Callable[..., Any])


def timed(label: str | None = None) -> Callable[[F], F]:
    """Decorator that logs execution time of the wrapped function."""
    def decorator(fn: F) -> F:
        name = label or fn.__qualname__

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            t0 = perf_counter()
            result = fn(*args, **kwargs)
            logger.debug("{} completed in {:.3f}s", name, perf_counter() - t0)
            return result

        return wrapper  # type: ignore[return-value]
    return decorator
