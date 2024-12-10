import time
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar
from prometheus_client import Histogram


T = TypeVar("T")


def calculate_execution_time(
    set_histogram: Histogram,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    def outer(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def inner(*args: Any, **kwargs: Any) -> T:
            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            end_time = time.perf_counter()

            execution_duration = (end_time - start_time) * 1_000_000
            set_histogram.observe(execution_duration)

            return result

        return inner

    return outer


def calculate_execution_time_sync(
    set_histogram: Histogram,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def outer(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> T:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()

            execution_duration = (end_time - start_time) * 1_000_000
            set_histogram.observe(execution_duration)

            return result

        return inner

    return outer
