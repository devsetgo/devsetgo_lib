# -*- coding: utf-8 -*-
import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger

from dsg_lib import logging_config

logging_config.config_log(
    logging_level="Debug", log_serializer=False, log_name="log.log"
)

app = FastAPI()


@app.get("/")
async def root():
    """
    Root endpoint of API
    Returns:
        Redrects to openapi document
    """
    # redirect to openapi docs
    logger.info("Redirecting to OpenAPI docs")
    response = RedirectResponse(url="/docs")
    return response


from dsg_lib.endpoints import system_health_endpoints  # , system_tools_endpoints

config_health = {
    "enable_status_endpoint": True,
    "enable_uptime_endpoint": True,
    "enable_heapdump_endpoint": True,
}
app.include_router(
    system_health_endpoints.create_health_router(config=config_health),
    prefix="/api/health",
    tags=["system-health"],
)
from dsg_lib.endpoints import system_tools_endpoints  # , system_tools_endpoints

config_tools = {
    "enable_email-validation": True,
}
app.include_router(
    system_tools_endpoints.create_tool_router(config=config_tools),
    prefix="/api/tools",
    tags=["system-tools"],
)
