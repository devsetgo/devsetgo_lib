# -*- coding: utf-8 -*-
# import datetime
# import logging
# import tempfile
# import unittest
# from pathlib import Path

# import pytest
# from _pytest.logging import caplog

# from dsg_lib.logging_config import config_log


# def some_func(var1, var2):
#     """
#     some function to test logging
#     """
#     if var1 < 1:
#         logging.warning(f"Oh no!")

#     return var1 + var2


# # class Test(unittest.TestCase):
# # `some_func` adds two numbers, and logs a warning if the first is < 1
# def test_some_func_logs_warning(caplog):
#     config_log()
#     assert some_func(-1, 3) == 2
#     assert "Oh no!" in caplog.text


# def test_exit_log_level():
#     with pytest.raises(ValueError) as e:
#         # The command to test
#         config_log(logging_level="bob")
#     # Here's the trick
#     assert e.type == ValueError
#     # assert e.value.code == 2


import unittest
from unittest.mock import patch, MagicMock
from dsg_lib.logging_config import config_log


class TestConfigLog(unittest.TestCase):
    @patch("dsg_lib.logging_config.logger")
    def test_config_log_with_valid_params(self, mock_logger):
        config_log(
            logging_directory="logs",
            log_name="app.log",
            logging_level="DEBUG",
            log_rotation="1 MB",
        )
        mock_logger.configure.assert_called_once()
        mock_logger.add.assert_called_once()

    def test_config_log_with_invalid_level(self):
        with self.assertRaises(ValueError):
            config_log(logging_level="INVALID")

    def test_config_log_with_invalid_log_name(self):
        with self.assertRaises(ValueError):
            config_log(log_name="invalid_name")

    @patch("dsg_lib.logging_config.logger")
    def test_config_log_with_app_name(self, mock_logger):
        config_log(app_name="my_app", append_app_name=True)
        mock_logger.configure.assert_called_once()
        mock_logger.add.assert_called_once()

    @patch("dsg_lib.logging_config.logger")
    def test_config_log_with_trace_id(self, mock_logger):
        config_log(enable_trace_id=True, append_trace_id=True)
        mock_logger.configure.assert_called_once()
        mock_logger.add.assert_called_once()


if __name__ == "__main__":
    unittest.main()
