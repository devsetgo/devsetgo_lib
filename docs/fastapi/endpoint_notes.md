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
