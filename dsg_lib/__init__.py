# -*- coding: utf-8 -*-

"""
This module is the entry point for the package. It imports the necessary functions and modules
from the package submodules so they can be used directly after importing the package.
"""

# Importing patterns from common_functions module
# Importing logging configuration from common_functions module
# Importing folder functions from common_functions module
# Importing file functions from common_functions module
# Importing calendar functions from common_functions module
from .common_functions import (
    calendar_functions,
    file_functions,
    folder_functions,
    logging_config,
    patterns,
)
# Importing database operations from database module
# Importing database configuration from database module
# Importing async database from database module
from .database import async_database, database_config, database_operations
# Importing system tools endpoints from endpoints module
# Importing system health endpoints from endpoints module
# Importing HTTP codes from endpoints module
from .endpoints import http_codes, system_health_endpoints, system_tools_endpoints
