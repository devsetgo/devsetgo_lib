# -*- coding: utf-8 -*-
import tracemalloc

import pytest
from robyn import AuthenticationHandler, Response, Robyn
from robyn.authentication import BearerGetter, Identity
from robyn.testing import TestClient as RobynTestClient

from dsg_lib.robyn_functions.system_health_endpoints import create_health_router


def make_client(config, prefix="/api/health", auth_handler=None):
    # A fresh app per test: Robyn's include_router mutates the app in place.
    app = Robyn(__file__)
    app.include_router(
        create_health_router(config, prefix=prefix, tags=["system-health"])
    )
    if auth_handler is not None:
        app.configure_authentication(auth_handler)
    return RobynTestClient(app)


def unauthorized():
    return Response(
        401, {"Content-Type": "application/json"}, '{"detail": "Unauthorized"}'
    )


@pytest.fixture
def tracing():
    tracemalloc.start()
    yield
    tracemalloc.stop()


def test_health_status():
    response = make_client({}).get("/api/health/status")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_get_uptime():
    response = make_client({}).get("/api/health/uptime")
    assert response.status_code == 200
    assert set(response.json()["uptime"]) == {"Days", "Hours", "Minutes", "Seconds"}


def test_endpoints_can_be_disabled():
    client = make_client(
        {"enable_status_endpoint": False, "enable_uptime_endpoint": False}
    )
    assert client.get("/api/health/status").status_code == 404
    assert client.get("/api/health/uptime").status_code == 404


def test_custom_prefix():
    client = make_client({}, prefix="/ops")
    assert client.get("/ops/status").json() == {"status": "UP"}
    assert client.get("/api/health/status").status_code == 404


def test_heapdump_disabled_by_default():
    response = make_client({}).get("/api/health/heapdump")
    assert response.status_code == 404


def test_get_heapdump(tracing):
    response = make_client({"enable_heapdump_endpoint": True}).get(
        "/api/health/heapdump"
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body["memory_use"]) == {"current", "peak"}
    for item in body["heap_dump"]:
        assert set(item) == {"filename", "lineno", "size", "count"}


def test_get_heapdump_error_returns_500():
    client = make_client({"enable_heapdump_endpoint": True})
    # create_health_router starts tracing; stopping it makes take_snapshot fail.
    tracemalloc.stop()
    response = client.get("/api/health/heapdump")
    assert response.status_code == 500
    assert response.json()["detail"].startswith("Error in get_heapdump:")


def test_heapdump_middleware_denies_unauthorized():
    client = make_client(
        {
            "enable_heapdump_endpoint": True,
            "heapdump_middlewares": [lambda request: unauthorized()],
        }
    )
    response = client.get("/api/health/heapdump")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_heapdump_middlewares_run_in_order_sync_and_async(tracing):
    calls = []

    def first(request):
        calls.append("first")
        return request

    async def second(request):
        calls.append("second")
        return None

    client = make_client(
        {"enable_heapdump_endpoint": True, "heapdump_middlewares": [first, second]}
    )
    response = client.get("/api/health/heapdump")
    assert response.status_code == 200
    assert calls == ["first", "second"]


def test_heapdump_middleware_short_circuit_skips_later_middlewares():
    calls = []

    def deny(request):
        calls.append("deny")
        return unauthorized()

    def never(request):  # pragma: no cover - must not run
        calls.append("never")
        return request

    client = make_client(
        {"enable_heapdump_endpoint": True, "heapdump_middlewares": [deny, never]}
    )
    assert client.get("/api/health/heapdump").status_code == 401
    assert calls == ["deny"]


def test_heapdump_middleware_realistic_api_key_pattern(tracing):
    # Mirrors the module docstring: the host app supplies its own header check.
    async def verify_admin(request):
        if request.headers.get("x-api-key") != "expected-secret":
            return unauthorized()
        return request

    client = make_client(
        {"enable_heapdump_endpoint": True, "heapdump_middlewares": [verify_admin]}
    )
    assert client.get("/api/health/heapdump").status_code == 401
    assert (
        client.get("/api/health/heapdump", headers={"x-api-key": "wrong"}).status_code
        == 401
    )
    response = client.get(
        "/api/health/heapdump", headers={"x-api-key": "expected-secret"}
    )
    assert response.status_code == 200
    assert "heap_dump" in response.json()


class TokenAuthHandler(AuthenticationHandler):
    def authenticate(self, request):
        token = self.token_getter.get_token(request)
        return Identity(claims={"user": "admin"}) if token == "good-token" else None


def test_heapdump_auth_required(tracing):
    client = make_client(
        {"enable_heapdump_endpoint": True, "heapdump_auth_required": True},
        auth_handler=TokenAuthHandler(token_getter=BearerGetter()),
    )
    assert client.get("/api/health/heapdump").status_code == 401
    assert (
        client.get(
            "/api/health/heapdump", headers={"Authorization": "Bearer bad-token"}
        ).status_code
        == 401
    )
    response = client.get(
        "/api/health/heapdump", headers={"Authorization": "Bearer good-token"}
    )
    assert response.status_code == 200
    # auth_required only applies to the heapdump route.
    assert client.get("/api/health/status").status_code == 200


def test_heapdump_auth_required_combined_with_middlewares(tracing):
    def deny(request):
        return Response(403, {}, "Forbidden")

    client = make_client(
        {
            "enable_heapdump_endpoint": True,
            "heapdump_auth_required": True,
            "heapdump_middlewares": [deny],
        },
        auth_handler=TokenAuthHandler(token_getter=BearerGetter()),
    )
    assert client.get("/api/health/heapdump").status_code == 401
    response = client.get(
        "/api/health/heapdump", headers={"Authorization": "Bearer good-token"}
    )
    assert response.status_code == 403


def test_heapdump_settings_ignored_when_disabled():
    client = make_client(
        {
            "heapdump_auth_required": True,
            "heapdump_middlewares": [lambda request: unauthorized()],
        }
    )
    assert client.get("/api/health/heapdump").status_code == 404


def test_router_without_heapdump_does_not_start_tracemalloc():
    from unittest.mock import patch

    with patch("dsg_lib.web_common.health.tracemalloc") as mock_tm:
        create_health_router({"enable_status_endpoint": True})
    mock_tm.start.assert_not_called()
