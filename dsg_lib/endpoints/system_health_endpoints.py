# -*- coding: utf-8 -*-
"""
This module provides a configurable health endpoint for the application. It includes the following routes:

- `/api/health/status`: Returns the status of the application. If the application is running, it will return `{"status": "UP"}`. This endpoint can be enabled or disabled using the configuration.

- `/api/health/uptime`: Returns the uptime of the application in a dictionary with the keys "Days", "Hours", "Minutes", and "Seconds". The uptime is calculated from the time the application was started. This endpoint can be enabled or disabled using the configuration.

- `/api/health/heapdump`: Returns a heap dump of the application. The heap dump is a list of dictionaries, each representing a line of code. Each dictionary includes the filename, line number, size of memory consumed, and the number of times the line is referenced. This endpoint can be enabled or disabled using the configuration.

Usage:

```python
from FastAPI import FastAPI
from devsetgo_toolkit import system_health_endpoints

app = FastAPI()

# User configuration
config = {
    "enable_status_endpoint": True,
    "enable_uptime_endpoint": False,
    "enable_heapdump_endpoint": True,
}

# Health router
health_router = system_health_endpoints.create_health_router(config)
app.include_router(health_router, prefix="/api/health", tags=["system-health"])
```
"""

# Import necessary modules
import time
import tracemalloc

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import ORJSONResponse

from devsetgo_toolkit.endpoints.http_codes import generate_code_dict

# Importing database connector module
from ..logger import logger

# import logging as logger

# Store the start time of the application
app_start_time = time.time()

# TODO: determine method to shutdown/restart python application

status_response = generate_code_dict([400, 405, 500], description_only=False)


def create_health_router(config: dict):
    """
    Create a health router with the following endpoints:

    - `/status`: Returns the status of the application. This endpoint can be enabled or disabled using the `enable_status_endpoint` key in the configuration.

    - `/uptime`: Returns the uptime of the application. This endpoint can be enabled or disabled using the `enable_uptime_endpoint` key in the configuration.

    - `/heapdump`: Returns a heap dump of the application. This endpoint can be enabled or disabled using the `enable_heapdump_endpoint` key in the configuration.

    Args:
        config (dict): A dictionary with the configuration for the endpoints. Each key should be the name of an endpoint (e.g., `enable_status_endpoint`) and the value should be a boolean indicating whether the endpoint is enabled or not.

    Returns:
        APIRouter: A FastAPI router with the configured endpoints.
    """
    # Create a new router
    router = APIRouter()

    # Check if the status endpoint is enabled in the configuration
    if config.get("enable_status_endpoint", True):
        # Define the status endpoint
        @router.get(
            "/status",
            tags=["system-health"],
            status_code=status.HTTP_200_OK,
            response_class=ORJSONResponse,
            responses=status_response,
        )
        async def health_status():
            """
            GET status, uptime, and current datetime

            Returns:
                dict -- [status: UP, uptime: seconds current_datetime: datetime.now]
            """
            # Log the status request
            logger.info("Health status of up returned")
            # Return a dictionary with the status of the application
            return {"status": "UP"}

    # Check if the uptime endpoint is enabled in the configuration
    if config.get("enable_uptime_endpoint", True):
        # Define the uptime endpoint
        @router.get("/uptime", response_class=ORJSONResponse, responses=status_response)
        async def get_uptime():
            """
            Calculate and return the uptime of the application.
            ...
            """
            # Calculate the total uptime in seconds
            # This is done by subtracting the time when the application started from the current time
            uptime_seconds = time.time() - app_start_time

            # Convert the uptime from seconds to days, hours, minutes, and seconds
            days, rem = divmod(uptime_seconds, 86400)
            hours, rem = divmod(rem, 3600)
            minutes, seconds = divmod(rem, 60)

            # Log the uptime
            logger.info(
                f"Uptime: {int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {round(seconds, 2)} seconds"
            )

            # Return a dictionary with the uptime
            # The dictionary has keys for days, hours, minutes, and seconds
            return {
                "uptime": {
                    "Days": int(days),
                    "Hours": int(hours),
                    "Minutes": int(minutes),
                    "Seconds": round(seconds, 2),
                }
            }

    if config.get("enable_heapdump_endpoint", True):

        @router.get(
            "/heapdump", response_class=ORJSONResponse, responses=status_response
        )
        async def get_heapdump():
            """
            Add the following to use heapdump:

            import tracemalloc to main FastAPI file

            To the fastAPI start up
            tracemalloc.start()

            To the fastAPI shutdown
            tracemalloc.stop()
            """

            try:
                # Take a snapshot of the current memory usage
                snapshot = tracemalloc.take_snapshot()
                # Get the top 10 lines consuming memory
                top_stats = snapshot.statistics("traceback")

                heap_dump = []
                for stat in top_stats[:10]:
                    # Get the first frame from the traceback
                    frame = stat.traceback[0]
                    # Add the frame to the heap dump
                    heap_dump.append(
                        {
                            "filename": frame.filename,
                            "lineno": frame.lineno,
                            "size": stat.size,
                            "count": stat.count,
                        }
                    )

                logger.debug(f"Heap dump returned {heap_dump}")
                # Return the heap dump
                return {"heap_dump": heap_dump}
            except Exception as ex:
                logger.error(f"Error in get_heapdump: {ex}")
                raise HTTPException(
                    status_code=500, detail=f"Error in get_heapdump: {ex}"
                )

    return router
