# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch

from dsg_lib.common_functions.logging_config import config_log


class TestConfigLog(unittest.TestCase):
    @patch("dsg_lib.common_functions.logging_config.logger")
    def test_config_log_with_valid_params(self, mock_logger):
        config_log(
            logging_directory="log",
            log_name="log",
            logging_level="INFO",
            log_rotation="2 MB",
            log_retention="30 days",
            log_backtrace=False,
            log_format=None,
            log_serializer=False,
            log_diagnose=False,
            app_name=None,
            append_app_name=False,
            enqueue=True,
            intercept_standard_logging=True,
            multiprocess=True,
        )
        mock_logger.configure.assert_called_once()
        mock_logger.add.assert_called_once()

    def test_config_log_with_invalid_level(self):
        with self.assertRaises(ValueError):
            config_log(logging_level="INVALID")

    # def test_config_log_with_invalid_log_name(self):
    #     with self.assertRaises(ValueError):
    #         config_log(log_name="invalid_name")

    @patch("dsg_lib.common_functions.logging_config.logger")
    def test_config_log_with_app_name(self, mock_logger):
        config_log(app_name="my_app", append_app_name=True)
        mock_logger.configure.assert_called_once()
        mock_logger.add.assert_called_once()


if __name__ == "__main__":
    unittest.main()
