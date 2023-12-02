# -*- coding: utf-8 -*-

"""
This module is the entry point for the package. It imports the necessary functions and modules
from the package submodules so they can be used directly after importing the package.
"""

# Importing calendar functions from common_functions module
from .common_functions import calendar_functions

# Importing file functions from common_functions module
from .common_functions import file_functions

# Importing folder functions from common_functions module
from .common_functions import folder_functions

# Importing logging configuration from common_functions module
from .common_functions import logging_config

# Importing patterns from common_functions module
from .common_functions import patterns

# Importing async database from database module
from .database import async_database

# Importing database configuration from database module
from .database import database_config

# Importing database operations from database module
from .database import database_operations

# Importing HTTP codes from endpoints module
from .endpoints import http_codes

# Importing system health endpoints from endpoints module
from .endpoints import system_health_endpoints

# Importing system tools endpoints from endpoints module
from .endpoints import system_tools_endpoints
