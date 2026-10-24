# -*- coding: utf-8 -*-
"""
Minimal FastAPI app mounting only dsg_lib's routers, used by
speedtest/endpoint_bench.py. Run directly with:

    DSG_BENCH_PORT=5055 python speedtest/apps/fastapi_app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uvicorn  # noqa: E402
from _common import (  # noqa: E402
    CODES,
    HEALTH_CONFIG,
    PORT,
    ROBOTS_CONFIG,
    configure_logging,
)
from fastapi import FastAPI  # noqa: E402
from loguru import logger  # noqa: E402

from dsg_lib.fastapi_functions import default_endpoints, system_health_endpoints  # noqa: E402
from dsg_lib.web_common.http_codes import generate_code_dict  # noqa: E402

configure_logging()

app = FastAPI()
app.include_router(
    system_health_endpoints.create_health_router(HEALTH_CONFIG), prefix="/api/health"
)
app.include_router(default_endpoints.create_default_router(ROBOTS_CONFIG))


@app.get("/codes")
async def codes():
    return generate_code_dict(CODES, description_only=True)


@app.get("/log")
async def log_line():
    # One INFO line per request: the cost a host pays for request logging.
    logger.info("bench request handled {}", 1)
    return {"logged": True}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning", access_log=False)
