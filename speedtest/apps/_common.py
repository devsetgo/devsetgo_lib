# -*- coding: utf-8 -*-
"""Settings shared by the benchmark target apps (read from env vars)."""
import os

PORT = int(os.environ.get("DSG_BENCH_PORT", "5055"))
LOG_DIR = os.environ.get("DSG_BENCH_LOG_DIR", "log")

# The health router config every bench app uses. heapdump stays off, as in a
# typical production deployment, so tracemalloc is not running.
HEALTH_CONFIG = {
    "enable_status_endpoint": True,
    "enable_uptime_endpoint": True,
    "enable_heapdump_endpoint": False,
}
ROBOTS_CONFIG = [{"bot": "GPTBot", "allow": False}, {"bot": "Googlebot", "allow": True}]
CODES = [200, 400, 404, 500]


def configure_logging():
    """Log the way a host app would: INFO to the rotating file sink."""
    from dsg_lib.common_functions.logging_config import config_log

    config_log(logging_directory=LOG_DIR, log_name="bench", logging_level="INFO")
