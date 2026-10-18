# -*- coding: utf-8 -*-
"""
Re-export of `dsg_lib.web_common.http_codes` for Robyn applications.

The HTTP status code helpers are framework-neutral. This module mirrors
`dsg_lib.fastapi_functions.http_codes` so Robyn apps can import from a
Robyn-named package. Pass `generate_code_dict(codes, description_only=True)`
to a Robyn route's `responses=` argument to document error responses in the
OpenAPI spec.

Example:
```python
from dsg_lib.robyn_functions import http_codes

print(http_codes.generate_code_dict([200, 404], description_only=True))
# {200: 'OK', 404: 'Not Found'}
```
"""

from dsg_lib.web_common.http_codes import (
    ALL_HTTP_CODES,
    DELETE_CODES,
    GET_CODES,
    PATCH_CODES,
    POST_CODES,
    PUT_CODES,
    common_codes,
    generate_code_dict,
)

__all__ = [
    "ALL_HTTP_CODES",
    "DELETE_CODES",
    "GET_CODES",
    "PATCH_CODES",
    "POST_CODES",
    "PUT_CODES",
    "common_codes",
    "generate_code_dict",
]
