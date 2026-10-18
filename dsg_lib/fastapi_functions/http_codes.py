# -*- coding: utf-8 -*-
"""
Backward-compatible re-export of `dsg_lib.web_common.http_codes`.

The HTTP status code helpers are framework-neutral and now live in
`dsg_lib.web_common` so the FastAPI and Robyn helpers can share them. This
module keeps `from dsg_lib.fastapi_functions import http_codes` working.

Example:
```python
from dsg_lib.fastapi_functions import http_codes

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
