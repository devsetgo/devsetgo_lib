# -*- coding: utf-8 -*-
# from loguru import logger
import importlib.util
import logging
import logging as logger

import pytest

# Robyn has no build for every Python version this library supports (e.g. no
# cp315 wheel or sdist yet), so it is left out of the dev/[all] installs there.
# Skip collecting its test modules instead of failing on `import robyn`.
collect_ignore_glob = []
if importlib.util.find_spec("robyn") is None:
    collect_ignore_glob.append("test_endpoints/test_robyn_*.py")


@pytest.fixture
def caplog(_caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message} {extra}")
    yield _caplog
    logger.remove(handler_id)
