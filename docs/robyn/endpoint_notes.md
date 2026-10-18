# Robyn Endpoint Notes

`dsg_lib.robyn_functions` mirrors `dsg_lib.fastapi_functions`. Both are thin
adapters over the framework-neutral `dsg_lib.web_common` package, so the
robots.txt content, the uptime/heap dump payloads, and the HTTP code metadata
are identical across frameworks.

Install with:

```sh
pip install devsetgo-lib[robyn]
```

Requires Robyn `>=0.87.0`, the first release with `SubRouter(prefix=..., tags=...)`
and the `responses=` route argument.

**Python 3.15:** Robyn does not publish a Python 3.15 build yet (no wheel and
no source distribution), so it cannot be installed there. The `[all]` extra
skips Robyn on 3.15 so the rest of the library still installs, and
`pip install devsetgo-lib[robyn]` on 3.15 fails until Robyn ships support.

## Differences from the FastAPI helpers

| | FastAPI | Robyn |
|---|---|---|
| Router type | `APIRouter` | `SubRouter` |
| Prefix / tags | `app.include_router(router, prefix=..., tags=...)` | `create_health_router(config, prefix=..., tags=...)`, then `app.include_router(router)` |
| Securing `/heapdump` | `heapdump_dependencies: [Depends(...)]` | `heapdump_middlewares: [callable]` and/or `heapdump_auth_required: True` |
| Heap dump error | `HTTPException(500, detail=...)` | `Response(500)` with JSON body `{"detail": ...}` |
| `responses=` shape | `generate_code_dict(codes)` | `generate_code_dict(codes, description_only=True)` |

## Securing `/heapdump`

`/heapdump` is disabled by default because it discloses internal file paths
and memory usage. As with the FastAPI version, the library implements no
authentication of its own. It hooks into the auth your app already has.

- **`heapdump_middlewares`**: a list of callables taking the Robyn `Request`.
  They run in order before the dump is taken. Return a `Response` to reject the
  request; return the request (or `None`) to continue. Sync and async are both
  supported.
- **`heapdump_auth_required`**: sets `auth_required=True` on the route, so the
  `AuthenticationHandler` registered with `app.configure_authentication(...)`
  must accept the request. Robyn raises `AuthenticationNotConfiguredError` if no
  handler is configured.

When both are set, authentication runs first, then the middlewares.

The middlewares run inside the route handler rather than through
`router.before_request("/heapdump")`. Robyn keeps a single route-level
middleware per path, and `auth_required=True` already uses that slot, so
registering a second one would silently replace the first.
