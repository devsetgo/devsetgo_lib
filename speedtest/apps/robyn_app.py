# -*- coding: utf-8 -*-
"""
Minimal Robyn app mounting only dsg_lib's routers, used by
speedtest/endpoint_bench.py. Run directly with:

    DSG_BENCH_PORT=5056 python speedtest/apps/robyn_app.py --processes 1 --workers 1
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    CODES,
    HEALTH_CONFIG,
    PORT,
    ROBOTS_CONFIG,
    configure_logging,
)
from loguru import logger  # noqa: E402
from robyn import Robyn  # noqa: E402

from dsg_lib.robyn_functions import default_endpoints, system_health_endpoints  # noqa: E402
from dsg_lib.web_common.http_codes import generate_code_dict  # noqa: E402

configure_logging()

app = Robyn(__file__)
app.include_router(
    system_health_endpoints.create_health_router(HEALTH_CONFIG, prefix="/api/health")
)
app.include_router(default_endpoints.create_default_router(ROBOTS_CONFIG))


@app.get("/codes")
def codes(request):
    # Robyn's JSON serializer only accepts str dict keys.
    return {str(k): v for k, v in generate_code_dict(CODES, description_only=True).items()}


@app.get("/log")
def log_line(request):
    # One INFO line per request: the cost a host pays for request logging.
    logger.info("bench request handled {}", 1)
    return {"logged": True}


if __name__ == "__main__":
    app.start(host="127.0.0.1", port=PORT)
