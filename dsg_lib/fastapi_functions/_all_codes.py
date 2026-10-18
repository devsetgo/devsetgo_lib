# -*- coding: utf-8 -*-
"""
Backward-compatible re-export of `dsg_lib.web_common._all_codes`.

`ALL_HTTP_CODES` is framework-neutral and now lives in `dsg_lib.web_common` so
the FastAPI and Robyn helpers can share it. This module keeps the old import
path working.
"""
from dsg_lib.web_common._all_codes import ALL_HTTP_CODES

__all__ = ["ALL_HTTP_CODES"]
