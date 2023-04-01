# -*- coding: utf-8 -*-
"""
configuration of loguru logging
includes intercepter for standard python logging
all configuration values are optional and have defaults
"""
import logging  # importing standard library logging module
from pathlib import Path  # importing the Path class from the pathlib module
from uuid import uuid4  # importing the uuid4 function from the uuid module

from loguru import logger  # importing the logger function from the loguru module


def config_log(
    logging_directory: str = "log",  # directory where log file will be stored
    log_name: str = "log.json",  # name of the log file
    logging_level: str = "INFO",  # level of logging
    log_rotation: str = "10 MB",  # size at which log file should be rotated
    log_retention: str = "30 days",  # how long logging data should be retained
    log_backtrace: bool = False,  # whether backtraces should be logged
    log_format: str = "'time': '{time:YYYY-MM-DD HH:mm:ss.SSSSSS}', 'level': '{level: <8}', 'name': '{name}', 'function': '{function}', 'line': '{line}', 'message': '{message}',",  # format of log messages
    log_serializer: bool = True,  # whether the log should be serialized
    log_diagnose: bool = False,  # whether to show logging diagnostics
    app_name: str = None,  # name of the application being logged
    append_app_name: bool = False,  # whether to append the application name to the log file name
    append_trace_id: bool = False,  # whether to append a trace ID to the log file name
    enable_trace_id: bool = False,  # whether to enable tracing for the log file
):
    """
    Configure and set up a logger using the loguru package.
    :param logging_directory: str, directory where log file will be stored
    :param log_name: str, name of the log file
    :param logging_level: str, level of logging
    :param log_rotation: str, size at which log file should be rotated
    :param log_retention: str, how long logging data should be retained
    :param log_backtrace: bool, whether backtraces should be logged
    :param log_format: str, format of log messages
    :param log_serializer: bool, whether the log should be serialized
    :param log_diagnose: bool, whether to show logging diagnostics
    :param app_name: str, name of the application being logged
    :param append_app_name: bool, whether to append the application name to the log file name
    :param append_trace_id: bool, whether to append a trace ID to the log file name
    :param enable_trace_id: bool, whether to enable tracing for the log file
    :return: None
    """

    log_levels: list = [
        "DEBUG",
        "INFO",
        "ERROR",
        "WARNING",
        "CRITICAL",
    ]  # valid logging levels
    if logging_level.upper() not in log_levels:  # check if logging level is valid
        raise ValueError(
            f"Invalid logging level: {logging_level}. Valid levels are: {log_levels}"
        )

    trace_id: str = str(uuid4())  # generate unique trace ID
    logger.configure(
        extra={"app_name": app_name, "trace_id": trace_id}
    )  # configure logger with trace ID and app name

    if app_name is not None:  # if app name is specified
        log_format = "app_name: {extra[app_name]}"  # change log format to

    if enable_trace_id is True:  # if tracing is enabled
        log_format = "trace_id: {extra[trace_id]}"  # change log format to show trace ID

    logger.remove()  # remove any previously added sinks

    if not log_name.endswith(
        (".log", ".json")
    ):  # check if log name ends with .log or .json
        error_message = f"log_name must end with .log or .json - {log_name}"
        logging.error(error_message)
        raise ValueError(error_message)

    if (
        append_app_name is True and app_name is not None
    ):  # if append app name is True and app name is not None
        log_name = log_name.replace(
            ".", f"_{app_name}."
        )  # append application name to log file name
    if append_trace_id is True:  # if append trace ID is True
        log_name = log_name.replace(
            ".", f"_{trace_id}."
        )  # append trace ID to log file name

    log_path = (
        Path.cwd().joinpath(logging_directory).joinpath(log_name)
    )  # create log file path using the specified directory and log file name

    logger.add(
        log_path,  # log file path
        level=logging_level.upper(),  # logging level
        format=log_format,  # format of log messages
        enqueue=True,  # set to true for async or multiprocessing logging
        backtrace=log_backtrace,  # whether backtraces should be logged
        rotation=log_rotation,  # file size to rotate
        retention=log_retention,  # how long the logging data persists
        compression="zip",  # log rotation compression
        serialize=log_serializer,  # whether the log should be serialized
        diagnose=log_diagnose,  # whether to show logging diagnostics
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
