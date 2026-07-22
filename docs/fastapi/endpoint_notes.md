# FastAPI Endpoint Notes

This page is a flexible notes area for the FastAPI part of the library.

Use this page for:

- migration and breaking changes
- compatibility or dependency notes
- behavior clarifications
- operational details that are useful but do not belong in API reference pages

When needed, this same notes pattern can be repeated for other library sections.

---

## Endpoint Change Notes

### Next release (heapdump endpoint security) — version TBD at release time

#### Changed: `/heapdump` is now disabled by default, and can be secured via a `Depends(...)` dependency

`/heapdump` (in `create_health_router()`) discloses internal file paths and
memory usage, so it's no longer exposed unless explicitly enabled. This is
inspired by Spring Boot Actuator, which does not implement its own auth for
sensitive endpoints — it routes them through the application's existing
Spring Security filter chain. `dsg_lib` does the same via FastAPI's own
`Depends()` mechanism: the library implements no authentication of its own,
and instead lets your application supply whatever auth it already uses.

**What changed:**

- `enable_heapdump_endpoint` now defaults to `False` (previously `True`). You
  must explicitly set it to `True` to expose the endpoint at all.
- New `heapdump_dependencies` config key: a list of already-constructed
  FastAPI `Depends(...)` objects, attached to the `/heapdump` route via
  `dependencies=`. Optional — if omitted, an enabled `/heapdump` remains
  unauthenticated, matching today's behavior.
- `/status` and `/uptime` are unaffected: unchanged defaults, no new config
  keys, no new dependencies.

**Impact:**

- If your application relies on `/heapdump` being exposed without explicitly
  setting `enable_heapdump_endpoint: True`, it will start returning `404`
  after upgrading. Set `enable_heapdump_endpoint: True` explicitly to restore
  it, and add `heapdump_dependencies` to secure it.

**Before:**

```python
config = {"enable_heapdump_endpoint": True}
router = create_health_router(config)
# GET /api/health/heapdump -> 200, no auth required
```

**After:**

```python
from fastapi import Depends, Header, HTTPException

async def verify_admin(x_api_key: str = Header(...)):
    if x_api_key != "expected-secret":
        raise HTTPException(status_code=401, detail="Unauthorized")

config = {
    "enable_heapdump_endpoint": True,
    "heapdump_dependencies": [Depends(verify_admin)],
}
router = create_health_router(config)
# GET /api/health/heapdump            -> 401 (no/invalid key)
# GET /api/health/heapdump  with key  -> 200
```

---

### v2026.3.15.1

#### Removed: `ORJSONResponse` from health endpoints

FastAPI 0.131.0 (released 2026-02-22) officially deprecated `ORJSONResponse` and `UJSONResponse`. These custom response classes are no longer needed because FastAPI now serializes JSON directly via Pydantic, which is faster and requires no extra dependency.

**What changed:**

The `/status`, `/uptime`, and `/heapdump` routes in `create_health_router()` previously forced `response_class=ORJSONResponse`. That argument has been removed. The endpoints now use FastAPI's default `JSONResponse`.

**Impact:**

- Response payloads and HTTP status codes are unchanged.
- If your application code explicitly imports `ORJSONResponse` from `fastapi.responses`, you will receive a `FastAPIDeprecationWarning`. Switch to returning plain dicts or Pydantic models and let FastAPI handle serialization.

**Before (deprecated):**

```python
from fastapi.responses import ORJSONResponse

router.get("/status", response_class=ORJSONResponse)
```

**After:**

```python
# No import needed — return a dict or Pydantic model directly
router.get("/status")
```

---

## General Notes

Add non-breaking notes here as needed (for example, defaults, behavior details, or usage tips).

---

## Compatibility Notes

Track framework or dependency compatibility notes here when useful.
