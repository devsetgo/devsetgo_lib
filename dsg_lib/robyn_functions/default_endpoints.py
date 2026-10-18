# -*- coding: utf-8 -*-
"""
Default endpoints for a Robyn application, mirroring
`dsg_lib.fastapi_functions.default_endpoints`.

Example:
```python
from robyn import Robyn
from dsg_lib.robyn_functions import default_endpoints

app = Robyn(__file__)

config = [
    {"bot": "GPTBot", "allow": False},
    {"bot": "Googlebot", "allow": True},
]
app.include_router(default_endpoints.create_default_router(config))
# GET /robots.txt -> text/plain robots.txt built from config
```

Author: Mike Ryan
License: MIT
"""

from typing import Dict, List, Optional, Union

from robyn import Response, SubRouter

from dsg_lib.web_common.robots import build_robots_txt


def create_default_router(
    config: List[Dict[str, Union[str, bool]]],
    prefix: str = "",
    tags: Optional[List[str]] = None,
) -> SubRouter:
    """
    Creates a Robyn SubRouter with default endpoints, including a configurable
    robots.txt.

    Unlike FastAPI's `app.include_router(router, prefix=...)`, Robyn's
    `include_router` takes no prefix, so the prefix and OpenAPI tags are set
    here instead.

    Args:
        config (List[Dict[str, Union[str, bool]]]): A list of dictionaries
            specifying which bots are allowed or disallowed, e.g.
            `{"bot": "GPTBot", "allow": False}`.
        prefix (str): Path prefix for the routes. Defaults to `""` (root).
        tags (Optional[List[str]]): OpenAPI tags applied to every route.

    Returns:
        SubRouter: A Robyn SubRouter with the default endpoints. Register it
        with `app.include_router(router)`.
    """
    router = SubRouter(prefix=prefix, tags=tags)

    @router.get("/robots.txt")
    def robots_txt(request):
        """
        Generates a robots.txt file based on the provided configuration.

        Returns:
            Response: The robots.txt content as `text/plain`.
        """
        return Response(
            status_code=200,
            headers={"Content-Type": "text/plain"},
            description=build_robots_txt(config),
        )

    return router
