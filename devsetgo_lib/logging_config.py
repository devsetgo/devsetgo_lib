# -*- coding: utf-8 -*-
"""
configuration of loguru logging

"""
import logging
from pathlib import Path

from loguru import logger


def config_log(
    logging_directory: str,
    log_name: str,
    logging_level: str = None,
    log_rotation: str = None,
    log_retention: str = None,
):
    """
    Logging configuration and interceptor for standard python logging
    Args:
        logging_directory (str): [logging directory name]
        log_name (str): [description]
        logging_level (str, optional): [description]. Defaults to None.
        log_rotation (str, optional): [description]. Defaults to None.
        log_retention (str, optional): [description]. Defaults to None.
    """
    if logging_level is None:
        logging_level = "INFO"

    if log_rotation is None:
        log_rotation = "10 MB"

    if log_retention is None:
        log_retention = "14 days"

    # remove default logger
    logger.remove()
    # set file path
    log_path = Path.cwd().joinpath(logging_directory).joinpath(f"{log_name}.log")
    # log_path = p.joinpath("logfile").joinpath("log.log")
    # add new configuration
    logger.add(
        log_path,  # log file path
        level=logging_level.upper(),  # logging level
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",  # format of log
        enqueue=True,  # set to true for async or multiprocessing logging
        backtrace=False,  # turn to false if in production to prevent data leaking
        rotation=log_rotation,  # file size to rotate
        retention=log_retention,  # how long a the logging data persists
        compression="zip",  # log rotation compression
        serialize=False,  # if you want it json style, set to true. but also change the format
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

    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=config_settings.loguru_logging_level.upper(),
    )
