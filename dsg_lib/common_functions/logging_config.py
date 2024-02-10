# -*- coding: utf-8 -*-
"""
Configuration of loguru logging Includes interceptor for standard python logging
All configuration values are optional and have defaults

Usage Example: ```python from logging_config import config_log

config_log(
    logging_directory='logs',  # Directory where logs will be stored
    log_name='app.log',  # Name of the log file logging_level='DEBUG',  #
    Logging level log_rotation='100 MB',  # Log rotation size log_retention='30
    days',  # Log retention period log_backtrace=True,  # Enable backtrace
    log_format="<green>{time:YYYY-MM-DD HH:mm:ss.SSSSSS}</green> |
    <level>{level: <8}</level> |
    <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> -
    <level>{message}</level>",  # Log format log_serializer=False,  # Disable
    log serialization log_diagnose=True,  # Enable diagnose app_name='my_app', #
    Application name append_app_name=True  # Append application name to the log
    file name
)

logger.debug("This is a debug message") logger.info("This is an info message")
logger.error("This is an error message") logger.warning("This is a warning
message") logger.critical("This is a critical message") ```
"""

import logging
from pathlib import Path
from uuid import uuid4

from loguru import logger


def config_log(
    logging_directory: str = "log",
    log_name: str = "log.log",
    logging_level: str = "INFO",
    log_rotation: str = "100 MB",
    log_retention: str = "30 days",
    log_backtrace: bool = False,
    log_format: str = None,
    log_serializer: bool = False,
    log_diagnose: bool = False,
    app_name: str = None,
    append_app_name: bool = False,
):
    """
    Configure and set up a logger using the loguru package.

    Usage Example: ```python from logging_config import config_log

    # Configure the logger config_log(
        logging_directory='logs',  # Directory where logs will be stored
        log_name='app.log',  # Name of the log file logging_level='DEBUG',  #
        Logging level log_rotation='500 MB',  # Log rotation size
        log_retention='10 days',  # Log retention period log_backtrace=True,  #
        Enable backtrace log_format="<green>{time:YYYY-MM-DD
        HH:mm:ss.SSSSSS}</green> | <level>{level: <8}</level> |
        <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> -
        <level>{message}</level>",  # Log format log_serializer=False,  #
        Disable log serialization log_diagnose=True,  # Enable diagnose
        app_name='my_app',  # Application name append_app_name=True  # Append
        application name to the log file name
    )

    # Now you can use the logger in your application logger.debug("This is a
    debug message") logger.info("This is an info message") logger.error("This is
    an error message") This will configure the logger to log all messages with
    level DEBUG or higher to a file named 'debug.log'. ```
    """
    # Set default log format if not provided
    if log_format is None:  # pragma: no cover
        if log_serializer:  # pragma: no cover
            log_format = "'time': '{time:YYYY-MM-DD HH:mm:ss.SSSSSS}', 'level': '{level: <8}', 'name': '{name}', 'function': '{function}', 'line': '{line}', 'message': '{message}',"  # pragma: no cover
        else:  # pragma: no cover
            log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSSSSS}</green> | <level>{level: <8}</level> | <cyan> {name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"  # pragma: no cover

    # Validate logging level
    log_levels: list = ["DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL"]
    if logging_level.upper() not in log_levels:
        raise ValueError(
            f"Invalid logging level: {logging_level}. Valid levels are: {log_levels}"
        )

    # Generate unique trace ID
    trace_id: str = str(uuid4())
    logger.configure(extra={"app_name": app_name, "trace_id": trace_id})

    # Append app name to log format if provided
    if app_name is not None:
        log_format = "app_name: {extra[app_name]}"

    # Remove any previously added sinks
    logger.remove()

    # Validate log file extension
    if not log_name.endswith((".log", ".json")):
        error_message = f"log_name must end with .log or .json - {log_name}"
        logging.error(error_message)
        raise ValueError(error_message)

    # Append app name to log file name if required
    if append_app_name is True and app_name is not None:
        log_name = log_name.replace(".", f"_{app_name}.")

    # Construct log file path
    log_path = Path.cwd().joinpath(logging_directory).joinpath(log_name)

    # Add loguru logger with specified configuration
    logger.add(
        log_path,
        level=logging_level.upper(),
        format=log_format,
        enqueue=True,
        backtrace=log_backtrace,
        rotation=log_rotation,
        retention=log_retention,
        compression="zip",
        serialize=log_serializer,
        diagnose=log_diagnose,
    )

    class InterceptHandler(logging.Handler):
        """
        Interceptor for standard logging.

        This class intercepts standard Python logging messages and redirects
        them to the Loguru logger. It is used as a handler for the standard
        Python logger.

        Attributes:
            level (str): The minimum severity level of messages that this
            handler should handle.

        Usage Example: ```python from dsg_lib.logging_config import
        InterceptHandler import logging

        # Create a standard Python logger logger =
        logging.getLogger('my_logger')

        # Create an InterceptHandler handler = InterceptHandler()

        # Add the InterceptHandler to the logger logger.addHandler(handler)

        # Now, when you log a message using the standard Python logger, it will
        be intercepted and redirected to the Loguru logger logger.info('This is
        an info message') ```
        """

        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:  # pragma: no cover
                level = record.levelno  # pragma: no cover

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:  # pragma: no cover
                frame = frame.f_back  # pragma: no cover
                depth += 1  # pragma: no cover

            # Log the message using loguru
            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )  # pragma: no cover

    # Configure standard logging to use interceptor handler
    logging.basicConfig(handlers=[InterceptHandler()], level=logging_level.upper())

    # Add interceptor handler to all existing loggers
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).addHandler(InterceptHandler())

    # Set the root logger's level to the lowest level possible
    logging.getLogger().setLevel(logging.NOTSET)
