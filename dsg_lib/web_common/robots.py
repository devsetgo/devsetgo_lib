# -*- coding: utf-8 -*-
"""
Framework-neutral robots.txt generation used by the FastAPI and Robyn
`default_endpoints` routers.

Example:
```python
from dsg_lib.web_common.robots import build_robots_txt

print(build_robots_txt([{"bot": "GPTBot", "allow": False}]))
# User-agent: *
# User-agent: GPTBot
# Disallow: /
```

Author: Mike Ryan
License: MIT
"""

from typing import Dict, List, Union

from loguru import logger


def build_robots_txt(config: List[Dict[str, Union[str, bool]]]) -> str:
    """
    Build robots.txt content from a list of bot rules.

    Args:
        config (List[Dict[str, Union[str, bool]]]): Entries of the form
            `{"bot": "<user agent>", "allow": <bool>}`. `allow` defaults to
            `True`; entries without a `bot` are skipped.

    Returns:
        str: The robots.txt body, lines separated by `\\n`.
    """
    logger.info("Generating robots.txt")
    lines = ["User-agent: *"]
    for entry in config:
        bot = entry.get("bot")
        allow = entry.get("allow", True)
        if bot:
            logger.debug(f"Configuring bot: {bot}, Allow: {allow}")
            lines.append(f"User-agent: {bot}")
            lines.append("Disallow: /" if not allow else "Allow: /")
    logger.info("robots.txt generated successfully")
    return "\n".join(lines)
