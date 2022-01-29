# -*- coding: utf-8 -*-
import datetime
import tempfile
import unittest

import pytest
from _pytest.logging import caplog
from dsg_lib.logging_config import config_log
import logging


def some_func(var1, var2):
    """
    some function to test logging
    """
    if var1 < 1:
        logging.warning(f"Oh no!")

    return var1 + var2


# class Test(unittest.TestCase):
# `some_func` adds two numbers, and logs a warning if the first is < 1
def test_some_func_logs_warning(caplog):
    config_log()
    assert some_func(-1, 3) == 2
    assert "Oh no!" in caplog.text


def test_exit():

    with pytest.raises(SystemExit) as e:
        # The command to test
        config_log(logging_level="bob")
    # Here's the trick
    assert e.type == SystemExit
    # assert e.value.code == 2
