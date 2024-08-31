# -*- coding: utf-8 -*-
"""
DevSetGo Library
=========

Author: Mike Ryan <mikeryan56@gmail.com>
License: MIT
"""
from datetime import date

__version__ = "0.14.3"
__author__ = "Mike Ryan"
__license__ = "MIT"
__copyright__ = f"Copyright© 2021-{date.today().year}"
__site__ = "https://github.com/devsetgo/devsetgo_lib"


# Import the library's modules
import logging

# Configure the library's logger
LOGGER = logging.getLogger("devsetgo_lib")
LOGGER.addHandler(logging.NullHandler())
LOGGER.propagate = False
