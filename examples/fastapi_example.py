from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import logging

from loguru import logger

from dsg_lib import logging_config

logging_config.config_log()

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

