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
    logging_directory: str = None,
    log_name: str = None,
    logging_level: str = None,
    log_rotation: str = None,
    log_retention: str = None,
    log_backtrace: bool = None,
    log_format: str = None,
    log_serializer: bool = None,
):
    """
    Logging configuration and interceptor for standard python logging

    Args:
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
    """

    # set logging directory
    if logging_directory is None:
        logging_directory = "logging"

    # set default log name
    if log_name is None:
        log_name = "log.log"

    # set default logging level
    if logging_level is None:
        logging_level = "INFO"

    # set default rotation size
    if log_rotation is None:
        log_rotation = "10 MB"

    # set defaul retention to 14 days
    if log_retention is None:
        log_retention = "14 days"

    # set default backtrace to false
    if log_backtrace is None:
        log_backtrace = False

    # set default logging format
    if log_format is None:
        log_format = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"

    # set default serializer to false
    if log_serializer is None:
        log_serializer = False

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
    class InterceptHandler(logging.Handler):
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
