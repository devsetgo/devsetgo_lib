# -*- coding: utf-8 -*-
"""
configuration of loguru logging
includes intercepter for standard python logging
all configuration values are optional and have defaults
"""
import logging
from pathlib import Path

from loguru import logger


def config_log(
    # app_enviorment: str,
    logging_directory: str = "logging",
    log_name: str = "log.log",
    logging_level: str = "INFO",
    log_rotation: str = "10 MB",
    log_retention: str = "14 days",
    log_backtrace: bool = False,
    log_format: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    log_serializer: bool = False,
    log_diagnose: bool = False,
):
    """
    Logging configuration and interceptor for standard python logging

    Args:
        app_enviorment (str): which enviorment the application is running in.
        logging_directory (str): [folder for logging]. Defaults to logging.
        log_name (str): [file name of log]
        logging_level (str, optional):
            [logging level - DEBUG, INFO, ERROR, WARNING, CRITICAL].
            Defaults to INFO.
        log_rotation (str, optional): [rotate log size]. Defaults to "10 MB".
        log_retention (str, optional): [how long to keep logs]. Defaults to "14 days".
        log_backtrace (bool, optional): [enable bactrace]. Defaults to False.
        log_format (str, optional): [format patter]. Defaults to
            "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}".
        log_serializer (bool, optional): [enable serialize]. Defaults to False.
        log_diagnose (bool, optional): [enable diagnose]. Defaults to False.
    """

    # # set default logging level
    log_levels: list = ["DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL"]
    if logging_level.upper() not in log_levels:
        # print and then log error if not a valid logging level
        print(f"logging_level {logging_level} not a valid level - {log_levels}")
        logger.critical(
            f"logging_level {logging_level} not a valid level - {log_levels}"
        )
        # exit application to prevent errors
        exit()

    # remove default logger
    logger.remove()

    # set file path
    log_path = Path.cwd().joinpath(logging_directory).joinpath(log_name)

    # add new configuration
    logger.add(
        log_path,  # log file path
        level=logging_level.upper(),  # logging level
        format=log_format,  # format of log
        enqueue=True,  # set to true for async or multiprocessing logging
        backtrace=log_backtrace,
        # turn to false if in production to prevent data leaking
        rotation=log_rotation,  # file size to rotate
        retention=log_retention,  # how long a the logging data persists
        compression="zip",  # log rotation compression
        serialize=False,
        # if you want it json style, set to true. but also change the format
    )

    # intercept standard logging
    class InterceptHandler(logging.Handler):  # pragma: no cover
        """
        Interceptor for standard logging.
        Excluded from code coverage as it is tested in the test_logging_config.py
        """

        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    # add interceptor handler
    logging.basicConfig(
        handlers=[InterceptHandler()], level=logging_level.upper(),
    )
