# -*- coding: utf-8 -*-

"""
This module is the entry point for the package. It imports the necessary functions and modules
from the package submodules so they can be used directly after importing the package.
"""
from .common_functions import (
    calendar_functions,
    file_functions,
    folder_functions,
    logging_config,
    patterns,
)

# from .database import async_database, database_config, database_operations
# from .fastapi_endpoints import http_codes, system_health_endpoints
