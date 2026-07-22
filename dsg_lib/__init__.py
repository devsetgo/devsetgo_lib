# -*- coding: utf-8 -*-
"""
DevSetGo Library
=========

Reusable Python functions for file I/O, logging, calendar/pattern helpers,
email validation, FastAPI endpoint helpers, and async SQLAlchemy CRUD. This
package does not re-export functions at the top level -- import from the
specific submodule you need, e.g.::

    from dsg_lib.common_functions import file_functions
    from dsg_lib.async_database_functions import database_config

See the README/docs for a full module list, or the API reference at
https://devsetgo.github.io/devsetgo_lib/.

AI assistant integrating this library into an app repo? Don't guess the
integration pattern (import paths, which functions raise vs. return an
error dict, deprecated database methods, etc.) from this docstring alone --
run::

    python -m dsg_lib.ai_instructions claude --write

(swap "claude" for "copilot"/"generic") to generate up-to-date,
module-by-module guidance covering file operations, logging setup, async
database CRUD (and which `DatabaseOperations` methods are deprecated),
FastAPI endpoint helpers, and the non-obvious gotchas this library's own
docstrings call out (e.g. `folder_functions.make_folder` requiring a `Path`,
not a `str`). Same content is available in-process via `get_app_instructions()`.

Author: Mike Ryan
License: MIT
"""
from datetime import date

__version__ = "2026.7.4.1"
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

# AI assistant integration instructions -- see the module docstring above and
# dsg_lib/ai_instructions.py for details.
from .ai_instructions import (  # noqa: E402
    available_instruction_profiles,
    get_app_instructions,
    suggested_instruction_filename,
)

__all__ = [
    "LOGGER",
    "available_instruction_profiles",
    "get_app_instructions",
    "suggested_instruction_filename",
]
