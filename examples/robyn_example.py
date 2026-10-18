# -*- coding: utf-8 -*-
"""
# Robyn Example Module

This module demonstrates the DevSetGo Toolkit's Robyn helpers: a configurable
robots.txt endpoint and the system health endpoints, including a `/heapdump`
route secured by the application's own API-key check.

## Features

- **Default Endpoints**: `GET /robots.txt` built from a list of bot rules.
- **System Health Endpoints** under `/api/health`:
  - `GET /api/health/status` returns `{"status": "UP"}`.
  - `GET /api/health/uptime` returns days/hours/minutes/seconds of uptime.
  - `GET /api/health/heapdump` returns a tracemalloc heap dump, and requires an
    `x-api-key` header (rejected with 401 otherwise).
- **HTTP Codes**: documents error responses in the OpenAPI spec (`/docs`) via
  `http_codes.generate_code_dict(..., description_only=True)`.

## Usage

```sh
pip install devsetgo-lib[robyn]
make ex-robyn   # or: python examples/robyn_example.py

curl http://localhost:5000/robots.txt
curl http://localhost:5000/api/health/status
curl http://localhost:5000/api/health/uptime
curl -i http://localhost:5000/api/health/heapdump                          # 401
curl -H "x-api-key: change-me" http://localhost:5000/api/health/heapdump   # 200
```

Set `ROBYN_EXAMPLE_API_KEY` to change the expected key, and `PORT` to change the
port.

## License
This module is licensed under the MIT License.
"""

import json
import os
import secrets

from robyn import Response, Robyn

from dsg_lib.robyn_functions import (
    default_endpoints,
    http_codes,
    system_health_endpoints,
)

API_KEY = os.environ.get("ROBYN_EXAMPLE_API_KEY", "change-me")

app = Robyn(__file__)


def verify_api_key(request):
    """Reject the request with a 401 unless the x-api-key header matches."""
    provided = request.headers.get("x-api-key") or ""
    if not secrets.compare_digest(provided, API_KEY):
        return Response(
            status_code=401,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"detail": "Unauthorized"}),
        )
    return request


robots_config = [
    {"bot": "GPTBot", "allow": False},
    {"bot": "CCBot", "allow": False},
    {"bot": "Googlebot", "allow": True},
    {"bot": "Bingbot", "allow": True},
]
app.include_router(
    default_endpoints.create_default_router(robots_config, tags=["default"])
)

health_config = {
    "enable_status_endpoint": True,
    "enable_uptime_endpoint": True,
    "enable_heapdump_endpoint": True,
    "heapdump_middlewares": [verify_api_key],
}
app.include_router(
    system_health_endpoints.create_health_router(
        health_config, prefix="/api/health", tags=["system-health"]
    )
)


@app.get(
    "/", responses=http_codes.generate_code_dict([404, 500], description_only=True)
)
def index(request):
    """Root endpoint listing the example routes."""
    return {
        "routes": [
            "/robots.txt",
            "/api/health/status",
            "/api/health/uptime",
            "/api/health/heapdump",
            "/docs",
        ]
    }


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
