# -*- coding: utf-8 -*-
"""
Framework-neutral calculations behind the `/uptime` and `/heapdump` system
health endpoints, shared by the FastAPI and Robyn `system_health_endpoints`
routers.

Example:
```python
import time
import tracemalloc

from dsg_lib.web_common.health import calculate_uptime, get_heap_dump

start = time.time()
print(calculate_uptime(start))
# {"uptime": {"Days": 0, "Hours": 0, "Minutes": 0, "Seconds": 0.0}}

tracemalloc.start()
print(get_heap_dump()["memory_use"])
# {"current": "123,456", "peak": "789,012"}
```

Author: Mike Ryan
License: MIT
"""

import time
import tracemalloc
from typing import Any, Dict

from loguru import logger


def start_tracemalloc_for_heapdump(config: Dict[str, Any]) -> bool:
    """
    Start `tracemalloc` only when the `/heapdump` endpoint needs it.

    `tracemalloc` hooks every memory allocation in the whole process for as
    long as it runs, which slows allocation-heavy code by an order of
    magnitude. So the health routers only start it when
    `enable_heapdump_endpoint` is `True` and `start_tracemalloc` (default
    `True`) is not `False`. If tracing is already active (for example the
    host set `PYTHONTRACEMALLOC=25`), it is left alone so the host's
    frame depth is not reset to 1.

    Args:
        config (dict): The health router config.

    Returns:
        bool: True if this call started tracing, False otherwise.
    """
    if not config.get("enable_heapdump_endpoint", False):
        return False
    if not config.get("start_tracemalloc", True):
        return False
    if tracemalloc.is_tracing():
        return False
    tracemalloc.start()
    return True


def calculate_uptime(start_time: float) -> Dict[str, Dict[str, Any]]:
    """
    Calculate the uptime since `start_time`.

    Args:
        start_time (float): A `time.time()` timestamp taken at startup.

    Returns:
        dict: `{"uptime": {"Days": int, "Hours": int, "Minutes": int,
        "Seconds": float}}`, with seconds rounded to two decimals.
    """
    uptime_seconds = time.time() - start_time

    days, rem = divmod(uptime_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    logger.debug(
        "Uptime: {} days, {} hours, {} minutes, {} seconds",
        int(days),
        int(hours),
        int(minutes),
        round(seconds, 2),
    )

    return {
        "uptime": {
            "Days": int(days),
            "Hours": int(hours),
            "Minutes": int(minutes),
            "Seconds": round(seconds, 2),
        }
    }


def get_heap_dump(limit: int = 10) -> Dict[str, Any]:
    """
    Take a tracemalloc snapshot and return the top memory-consuming lines.

    `tracemalloc` must already be tracing (the health routers call
    `tracemalloc.start()` when they are created). Exceptions are not caught
    here, so each framework adapter can turn them into its own 500 response.

    Args:
        limit (int): How many of the largest allocation sites to return.
            Defaults to 10.

    Returns:
        dict: `{"memory_use": {"current": str, "peak": str}, "heap_dump":
        [{"filename", "lineno", "size", "count"}, ...]}`.

    Raises:
        RuntimeError: If tracemalloc is not tracing memory allocations.
    """
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("traceback")

    heap_dump = []
    for stat in top_stats[:limit]:
        frame = stat.traceback[0]
        heap_dump.append(
            {
                "filename": frame.filename,
                "lineno": frame.lineno,
                "size": stat.size,
                "count": stat.count,
            }
        )

    logger.debug("Heap dump returned {} allocation sites", len(heap_dump))
    memory_use = tracemalloc.get_traced_memory()
    return {
        "memory_use": {
            "current": f"{memory_use[0]:,}",
            "peak": f"{memory_use[1]:,}",
        },
        "heap_dump": heap_dump,
    }
