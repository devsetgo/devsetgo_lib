# -*- coding: utf-8 -*-
"""
Tests for the performance-related config_log options: intercept_level,
the enqueue default, log_to_file / log_to_stdout and background compression.
"""
import logging
import sys
from unittest.mock import patch

import pytest
from loguru import logger as real_logger

from dsg_lib.common_functions.logging_config import (
    InterceptHandler,
    SafeFileSink,
    config_log,
)


@pytest.fixture
def restore_stdlib_logging():
    root = logging.getLogger()
    saved_level, saved_handlers = root.level, list(root.handlers)
    saved = {
        name: (lg.handlers[:], lg.propagate, lg.level)
        for name, lg in logging.Logger.manager.loggerDict.items()
        if isinstance(lg, logging.Logger)
    }
    yield
    real_logger.remove()
    root.setLevel(saved_level)
    root.handlers = saved_handlers
    for name, (handlers, propagate, level) in saved.items():
        lg = logging.getLogger(name)
        lg.handlers, lg.propagate, lg.level = handlers, propagate, level


@pytest.fixture
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_root_level_follows_logging_level(restore_stdlib_logging, in_tmp):
    config_log(logging_level="INFO")
    assert logging.getLogger().level == logging.INFO
    assert logging.getLogger("some.library").isEnabledFor(logging.DEBUG) is False


def test_intercept_level_overrides_root_level(restore_stdlib_logging, in_tmp):
    config_log(logging_level="INFO", intercept_level="debug")
    assert logging.getLogger().level == logging.DEBUG


def test_invalid_intercept_level_raises(restore_stdlib_logging, in_tmp):
    with pytest.raises(ValueError, match="intercept level"):
        config_log(intercept_level="LOUD")


def test_one_shared_intercept_handler(restore_stdlib_logging, in_tmp):
    logging.getLogger("dsg_test.a")
    logging.getLogger("dsg_test.b")
    config_log()
    handlers = {
        id(h)
        for name in ("dsg_test.a", "dsg_test.b", "")
        for h in logging.getLogger(name or None).handlers
        if isinstance(h, InterceptHandler)
    }
    assert len(handlers) == 1


def test_stdlib_info_still_reaches_loguru(restore_stdlib_logging, in_tmp):
    config_log(log_to_file=False, log_to_stdout=True)
    received = []
    real_logger.add(received.append, level="INFO", format="{message}")
    logging.getLogger("dsg_test.forward").info("hello %s", "world")
    logging.getLogger("dsg_test.forward").debug("dropped")
    assert [m.strip() for m in received] == ["hello world"]


@patch("dsg_lib.common_functions.logging_config.logger")
def test_enqueue_defaults_to_false(mock_logger, restore_stdlib_logging, in_tmp):
    config_log()
    assert mock_logger.add.call_args.kwargs["enqueue"] is False


@patch("dsg_lib.common_functions.logging_config.logger")
def test_file_sink_compresses_in_background_by_default(mock_logger, restore_stdlib_logging, in_tmp):
    config_log()
    sink = mock_logger.add.call_args.args[0]
    assert isinstance(sink, SafeFileSink)
    assert sink.compress_in_background is True


@pytest.mark.parametrize(
    "to_file, to_stdout, expected",
    [
        (True, False, [SafeFileSink]),
        (False, True, [sys.stdout]),
        (True, True, [SafeFileSink, sys.stdout]),
    ],
)
@patch("dsg_lib.common_functions.logging_config.logger")
def test_sink_selection(mock_logger, to_file, to_stdout, expected, restore_stdlib_logging, in_tmp):
    config_log(log_to_file=to_file, log_to_stdout=to_stdout)
    sinks = [c.args[0] for c in mock_logger.add.call_args_list]
    assert len(sinks) == len(expected)
    for sink, want in zip(sinks, expected, strict=True):
        if want is sys.stdout:
            assert sink is sys.stdout
        else:
            assert isinstance(sink, want)


def test_no_sinks_raises(restore_stdlib_logging, in_tmp):
    with pytest.raises(ValueError, match="log_to_file or log_to_stdout"):
        config_log(log_to_file=False, log_to_stdout=False)


def test_stdout_only_creates_no_log_directory(restore_stdlib_logging, in_tmp):
    config_log(log_to_file=False, log_to_stdout=True)
    real_logger.info("to stdout")
    assert not (in_tmp / "log").exists()


def test_end_to_end_file_write(restore_stdlib_logging, in_tmp):
    config_log(log_name="e2e", log_format="{message}")
    real_logger.info("written")
    real_logger.remove()  # stop() closes the file
    assert (in_tmp / "log" / "e2e.log").read_text() == "written\n"
