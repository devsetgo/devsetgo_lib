# -*- coding: utf-8 -*-
"""
This module provides a configurable health endpoint for a Robyn application,
mirroring `dsg_lib.fastapi_functions.system_health_endpoints`. It includes the
following routes:

- `/status`: Returns `{"status": "UP"}`. Enabled by default.

- `/uptime`: Returns the uptime of the application in a dictionary with the
  keys "Days", "Hours", "Minutes", and "Seconds", calculated from the time the
  router was created. Enabled by default.

- `/heapdump`: Returns a tracemalloc heap dump (top 10 allocation sites plus
  current/peak memory). This endpoint discloses internal file paths and memory
  behavior, so it is **disabled by default** (`enable_heapdump_endpoint`
  defaults to `False`) and, once enabled, should be secured with the
  `heapdump_middlewares` and/or `heapdump_auth_required` config keys (see
  `create_health_router`).

Robyn's `include_router` takes no prefix argument, so the prefix (e.g.
`/api/health`) is passed to `create_health_router` instead.

Example:
    ```python
    from robyn import Response, Robyn
    from dsg_lib.robyn_functions import system_health_endpoints

    app = Robyn(__file__)

    # heapdump is sensitive (discloses internal file paths and memory usage),
    # so secure it with your app's own check. Return a Response to reject.
    def verify_admin(request):
        if request.headers.get("x-api-key") != "expected-secret":
            return Response(401, {"Content-Type": "application/json"}, '{"detail": "Unauthorized"}')
        return request

    config = {
        "enable_status_endpoint": True,
        "enable_uptime_endpoint": True,
        "enable_heapdump_endpoint": True,
        "heapdump_middlewares": [verify_admin],
    }

    health_router = system_health_endpoints.create_health_router(
        config, prefix="/api/health", tags=["system-health"]
    )
    app.include_router(health_router)

    # GET /api/health/status   -> {"status": "UP"}
    # GET /api/health/uptime   -> {"uptime": {"Days": 0, "Hours": 0, "Minutes": 1, "Seconds": 42.17}}
    # GET /api/health/heapdump -> 401 without the x-api-key header, otherwise
    #   {"memory_use": {"current": "123,456", "peak": "789,012"}, "heap_dump": [...]}
    ```

Author: Mike Ryan
License: MIT
"""

import inspect
import json
import time
import tracemalloc
from typing import List, Optional

from loguru import logger
from packaging import version as packaging_version

from dsg_lib.web_common.health import calculate_uptime, get_heap_dump
from dsg_lib.web_common.http_codes import generate_code_dict

# 0.87.0 is the first release with both SubRouter(prefix=..., tags=...) and
# the `responses=` route argument used below.
MIN_ROBYN_VERSION = "0.87.0"


def create_health_router(
    config: dict,
    prefix: str = "",
    tags: Optional[List[str]] = None,
):
    """
    Create a Robyn SubRouter with the following endpoints:

    - `/status`: Returns the status of the application. Toggle with
      `enable_status_endpoint`.

    - `/uptime`: Returns the uptime of the application. Toggle with
      `enable_uptime_endpoint`.

    - `/heapdump`: Returns a heap dump of the application. This endpoint
      discloses internal file paths and memory behavior, so it is **disabled
      by default**. Enable it with `enable_heapdump_endpoint`, and secure it
      with your application's own auth. This library implements no
      authentication itself. Two mechanisms are supported, and they can be
      combined:

        - `heapdump_middlewares`: callables taking the Robyn `Request`, run in
          order before the dump is taken. Return a `Response` to reject the
          request (e.g. a 401); return the request (or `None`) to continue.
          Sync and async callables are both supported.
        - `heapdump_auth_required`: sets Robyn's `auth_required=True` on the
          route, so the `AuthenticationHandler` your app registered with
          `app.configure_authentication(...)` must accept the request. If no
          handler is configured, Robyn raises `AuthenticationNotConfiguredError`.

    Args:
        config (dict): Endpoint configuration (see recognized keys below).
        prefix (str): Path prefix for all routes, e.g. `"/api/health"`.
            Defaults to `""` (root). Robyn's `include_router` takes no prefix,
            so it is set here.
        tags (Optional[List[str]]): OpenAPI tags applied to every route.

    Recognized config keys:
        - `enable_status_endpoint` (bool): Defaults to `True`.
        - `enable_uptime_endpoint` (bool): Defaults to `True`.
        - `enable_heapdump_endpoint` (bool): Defaults to `False` (opt-in,
          since this endpoint discloses internal file paths and memory usage).
        - `heapdump_middlewares` (list[Callable]): Optional request checks for
          `/heapdump`, described above. Ignored unless the heapdump endpoint
          is enabled.
        - `heapdump_auth_required` (bool): Defaults to `False`. Ignored unless
          the heapdump endpoint is enabled.

    Returns:
        SubRouter: A Robyn SubRouter with the configured endpoints. Register it
        with `app.include_router(router)`.

    Raises:
        ImportError: If the installed Robyn is older than `MIN_ROBYN_VERSION`.

    Example:
        ```python
        from robyn import Robyn
        from dsg_lib.robyn_functions import system_health_endpoints

        app = Robyn(__file__)
        health_router = system_health_endpoints.create_health_router(
            {"enable_uptime_endpoint": False}, prefix="/api/health"
        )
        app.include_router(health_router)
        # GET /api/health/status -> {"status": "UP"}
        ```
    """
    try:
        import robyn
        from robyn import Response, SubRouter
    except ImportError:  # pragma: no cover
        robyn = Response = SubRouter = None

    if robyn is not None and packaging_version.parse(
        robyn.__version__
    ) < packaging_version.parse(MIN_ROBYN_VERSION):
        raise ImportError(
            f"Robyn version >= {MIN_ROBYN_VERSION} required, run `pip install --upgrade robyn`"
        )  # pragma: no cover

    # Store the start time of the application
    app_start_time = time.time()

    # Robyn's `responses=` accepts {code: "description"} directly, so use the
    # description-only form rather than FastAPI's full dict shape.
    status_response = generate_code_dict([400, 405, 500], description_only=True)

    tracemalloc.start()
    router = SubRouter(prefix=prefix, tags=tags)

    if config.get("enable_status_endpoint", True):

        @router.get("/status", openapi_name="Health Status", responses=status_response)
        def health_status(request):
            """
            Returns the status of the application: `{"status": "UP"}`.
            """
            logger.info("Health status of up returned")
            return {"status": "UP"}

    if config.get("enable_uptime_endpoint", True):

        @router.get("/uptime", openapi_name="Uptime", responses=status_response)
        def get_uptime(request):
            """
            Returns the uptime of the application as
            `{"uptime": {"Days", "Hours", "Minutes", "Seconds"}}`.
            """
            return calculate_uptime(app_start_time)

    # Disabled by default: this endpoint discloses internal file paths and
    # memory usage, so it must be explicitly opted into (unlike status/uptime).
    if config.get("enable_heapdump_endpoint", False):
        heapdump_middlewares = list(config.get("heapdump_middlewares") or [])
        heapdump_auth_required = bool(config.get("heapdump_auth_required", False))
        heapdump_response = generate_code_dict(
            [400, 401, 403, 405, 500], description_only=True
        )

        # The middlewares run inside the handler instead of being registered
        # with router.before_request("/heapdump"): Robyn keeps a single route
        # middleware per path, and auth_required=True already occupies that
        # slot, so registering ours too would replace one with the other.
        @router.get(
            "/heapdump",
            auth_required=heapdump_auth_required,
            openapi_name="Heap Dump",
            responses=heapdump_response,
        )
        async def get_heapdump(request):
            """
            Returns a heap dump of the application: current/peak memory use
            and the top 10 allocation sites.

            Disabled unless `enable_heapdump_endpoint` is `True`; secure it via
            `heapdump_middlewares` and/or `heapdump_auth_required` (see
            `create_health_router`).
            """
            for middleware in heapdump_middlewares:
                result = middleware(request)
                if inspect.isawaitable(result):
                    result = await result
                if isinstance(result, Response):
                    return result
                if result is not None:
                    request = result

            try:
                return get_heap_dump()
            except Exception as ex:
                logger.error(f"Error in get_heapdump: {ex}")
                return Response(
                    status_code=500,
                    headers={"Content-Type": "application/json"},
                    description=json.dumps({"detail": f"Error in get_heapdump: {ex}"}),
                )

    return router
