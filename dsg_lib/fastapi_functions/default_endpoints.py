# -*- coding: utf-8 -*-
from typing import Dict, List

from fastapi import APIRouter, Response

from dsg_lib.web_common.robots import build_robots_txt


def create_default_router(config: List[Dict[str, str]]) -> APIRouter:
    """
    Creates a router with default endpoints, including a configurable robots.txt.

    Args:
        config (List[Dict[str, str]]): A list of dictionaries specifying which bots are allowed or disallowed.

    Returns:
        APIRouter: A FastAPI router with the default endpoints.
    """
    router = APIRouter()

    @router.get("/robots.txt", response_class=Response)
    async def robots_txt():
        """
        Generates a robots.txt file based on the provided configuration.

        Returns:
            Response: The robots.txt content.
        """
        robots_txt_content = build_robots_txt(config)
        return Response(robots_txt_content, media_type="text/plain")

    return router
