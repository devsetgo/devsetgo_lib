# -*- coding: utf-8 -*-
import datetime
import logging
import tempfile
import unittest
from pathlib import Path

import pytest
from _pytest.logging import caplog

from dsg_lib.logging_config import config_log


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


def test_exit_log_level():
    with pytest.raises(SystemExit) as e:
        # The command to test
        config_log(logging_level="bob")
    # Here's the trick
    assert e.type == SystemExit
    # assert e.value.code == 2


def test_exit_log_name():
    with pytest.raises(SystemExit) as e:
        # The command to test
        config_log(log_name="bob.l")
    # Here's the trick
    assert e.type == SystemExit


def test_exit_file_name():
    log_name = "log"
    app_name = "123"
    service_id = "456"
    config_log(
        log_name=f"{log_name}.log",
        app_name="123",
        service_id="456",
        append_app_name=True,
        append_service_id=True,
    )
    log_path = (
        Path.cwd().joinpath("log").joinpath(f"{log_name}_{app_name}_{service_id}.log")
    )
    test_name = str(log_path)
    assert log_path.exists()
    assert log_path.is_file()
    assert test_name.endswith(".log")
    assert "123" in test_name
    assert "456" in test_name
