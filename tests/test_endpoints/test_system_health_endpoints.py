# -*- coding: utf-8 -*-
import tracemalloc
from unittest.mock import patch

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

from dsg_lib.fastapi_functions.system_health_endpoints import create_health_router

# Create a FastAPI app for testing
app = FastAPI()
client = TestClient(app)

# User configuration
config = {
    # "enable_status_endpoint": False, # on by default
    # "enable_uptime_endpoint": False, # on by default
    "enable_heapdump_endpoint": True,  # must be explicit: defaults to False
}
# Health router
health_router = create_health_router(config)
app.include_router(health_router, prefix="/api/health", tags=["system-health"])


def test_health_status():
    response = client.get("/api/health/status")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_get_uptime():
    response = client.get("/api/health/uptime")
    assert response.status_code == 200
    assert "uptime" in response.json()
    # Check that the uptime dictionary has the expected keys
    assert set(response.json()["uptime"].keys()) == {
        "Days",
        "Hours",
        "Minutes",
        "Seconds",
    }


def test_get_heapdump():
    tracemalloc.start()  # Start tracing memory allocations
    response = client.get("/api/health/heapdump")
    tracemalloc.stop()  # Stop tracing memory allocations
    assert response.status_code == 200
    assert "heap_dump" in response.json()
    # Check that each item in the heap dump has the expected keys
    for item in response.json()["heap_dump"]:
        assert set(item.keys()) == {"filename", "lineno", "size", "count"}


@patch("tracemalloc.stop")  # , side_effect=TracemallocNotStartedError())
def test_get_heapdump_tracemalloc_error(mock_start):
    response = client.get("/api/health/heapdump")
    assert response.status_code == 500
    assert "detail" in response.json()


def test_heapdump_disabled_by_default():
    # No enable_heapdump_endpoint key at all -> the route must not be
    # registered, since it now defaults to disabled (opt-in).
    local_app = FastAPI()
    local_client = TestClient(local_app)
    router = create_health_router({})
    local_app.include_router(router, prefix="/api/health", tags=["system-health"])

    response = local_client.get("/api/health/heapdump")
    assert response.status_code == 404


def test_heapdump_dependency_denies_unauthorized():
    async def deny():
        raise HTTPException(status_code=401, detail="Unauthorized")

    local_app = FastAPI()
    local_client = TestClient(local_app)
    router = create_health_router(
        {
            "enable_heapdump_endpoint": True,
            "heapdump_dependencies": [Depends(deny)],
        }
    )
    local_app.include_router(router, prefix="/api/health", tags=["system-health"])

    response = local_client.get("/api/health/heapdump")
    assert response.status_code == 401


def test_heapdump_dependency_allows_authorized():
    async def allow():
        return True

    local_app = FastAPI()
    local_client = TestClient(local_app)
    router = create_health_router(
        {
            "enable_heapdump_endpoint": True,
            "heapdump_dependencies": [Depends(allow)],
        }
    )
    local_app.include_router(router, prefix="/api/health", tags=["system-health"])

    tracemalloc.start()
    response = local_client.get("/api/health/heapdump")
    tracemalloc.stop()
    assert response.status_code == 200
    body = response.json()
    assert "heap_dump" in body
    assert "memory_use" in body


def test_heapdump_dependency_realistic_api_key_pattern():
    # Mirrors the docstring example: the host app supplies its own
    # Header-based auth check as a Depends(...) - the library implements no
    # auth logic of its own.
    async def verify_admin(x_api_key: str = Header(...)):
        if x_api_key != "expected-secret":
            raise HTTPException(status_code=401, detail="Unauthorized")

    local_app = FastAPI()
    local_client = TestClient(local_app)
    router = create_health_router(
        {
            "enable_heapdump_endpoint": True,
            "heapdump_dependencies": [Depends(verify_admin)],
        }
    )
    local_app.include_router(router, prefix="/api/health", tags=["system-health"])

    # Missing header -> 422 (FastAPI's own required-header validation)
    response = local_client.get("/api/health/heapdump")
    assert response.status_code == 422

    # Wrong key -> 401 from our dependency
    response = local_client.get(
        "/api/health/heapdump", headers={"x-api-key": "wrong"}
    )
    assert response.status_code == 401

    # Correct key -> 200
    tracemalloc.start()
    response = local_client.get(
        "/api/health/heapdump", headers={"x-api-key": "expected-secret"}
    )
    tracemalloc.stop()
    assert response.status_code == 200
    assert "heap_dump" in response.json()


def test_status_and_uptime_remain_unaffected():
    # /status and /uptime are out of scope for this security change: they
    # stay enabled-by-default and unauthenticated regardless of heapdump config.
    local_app = FastAPI()
    local_client = TestClient(local_app)
    router = create_health_router({})
    local_app.include_router(router, prefix="/api/health", tags=["system-health"])

    assert local_client.get("/api/health/status").status_code == 200
    assert local_client.get("/api/health/uptime").status_code == 200
