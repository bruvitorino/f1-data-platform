from time import perf_counter
from typing import Callable


def measure_execution_time(
    function: Callable[[], None],
) -> float:
    """Execute a function and return its duration in seconds."""

    started_at = perf_counter()

    function()

    finished_at = perf_counter()

    return finished_at - started_at