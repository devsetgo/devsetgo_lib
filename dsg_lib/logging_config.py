# -*- coding: utf-8 -*-
"""
configuration of loguru logging
includes intercepter for standard python logging
all configuration values are optional and have defaults
"""
import logging
from pathlib import Path
from uuid import uuid4
from loguru import logger


def config_log(
    logging_directory: str = "log",
    log_name: str = "log.json",
    logging_level: str = "INFO",
    log_rotation: str = "10 MB",
    log_retention: str = "30 days",
    log_backtrace: bool = False,
    log_format: str = "'time': '{time:YYYY-MM-DD HH:mm:ss.SSSSSS}', 'level': '{level: <8}', 'name': '{name}', 'function': '{function}', 'line': '{line}', 'message': '{message}'",
    log_serializer: bool = True,
    log_diagnose: bool = False,
    app_name: str = None,
    append_app_name: bool = False,
    append_trace_id: bool = False,
    enable_trace_id: bool = False,
    append_service_id: bool = False,
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
        app_name (str, optional): [app name]. Defaults to None.
        append_app_name (bool, optional): [append app name to log file name].
        service_id (str, optional): [service id]. Defaults to None.
        append_service_name (bool, optional): [append service name to log file name].
    """

    # # set default logging level
    log_levels: list = ["DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL"]
    if logging_level.upper() not in log_levels:
        # raise an exception for invalid logging level
        raise ValueError(
            f"Invalid logging level: {logging_level}. Valid levels are: {log_levels}"
        )

    # set log format extras
    trace_id: str = str(uuid4())
    logger.configure(extra={"app_name": app_name, "trace_id": trace_id})

    # add app name to log format
    if app_name is not None:
        log_format = log_format + " | app_name={extra[app_name]}"

    # add trace_id to log format
    if enable_trace_id is True:
        log_format = log_format + " | trace_id={extra[trace_id]}"

    # remove default logger
    logger.remove()

    # set log file options
    if not log_name.endswith((".log", ".json")):
        error_message = f"log_name must end with .log or .json - {log_name}"
        logging.error(error_message)
        raise ValueError(error_message)

    # set app name in log file name
    if append_app_name is True and app_name is not None:
        # append app name to log file name
        log_name = log_name.replace(".", f"_{app_name}.")
    # set service name in log file name
    if append_trace_id is True:
        log_name = log_name.replace(".", f"_{trace_id}.")
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
        serialize=log_serializer,
        # if you want it json style, set to true. but also change the format
        diagnose=log_diagnose,
        # if you want to see the diagnose of the logging, set to true
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
        handlers=[InterceptHandler()],
        level=logging_level.upper(),
    )
