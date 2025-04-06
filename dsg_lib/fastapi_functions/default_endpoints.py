# -*- coding: utf-8 -*-
from typing import Dict, List

from fastapi import APIRouter, Response
from loguru import logger


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
        logger.info("Generating robots.txt")
        lines = ["User-agent: *"]
        for entry in config:
            bot = entry.get("bot")
            allow = entry.get("allow", True)
            if bot:
                logger.debug(f"Configuring bot: {bot}, Allow: {allow}")
                lines.append(f"User-agent: {bot}")
                lines.append("Disallow: /" if not allow else "Allow: /")
        robots_txt_content = "\n".join(lines)
        logger.info("robots.txt generated successfully")
        return Response(robots_txt_content, media_type="text/plain")

    return router
