# -*- coding: utf-8 -*-
"""
This module provides a comprehensive logging setup using the loguru library, facilitating easy logging management for Python applications.

The `config_log` function, central to this module, allows for extensive customization of logging behavior. It supports specifying the logging directory, log file name, logging level, and controls for log rotation, retention, and formatting among other features. Additionally, it offers advanced options like backtrace and diagnose for in-depth debugging, and the ability to append the application name to the log file for clearer identification.

Usage example:

    from dsg_lib.common_functions.logging_config import config_log

    config_log(
        logging_directory='logs',  # Directory for storing logs
        log_name='log',  # Base name for log files
        logging_level='DEBUG',  # Minimum logging level
        log_rotation='100 MB',  # Size threshold for log rotation
        log_retention='30 days',  # Duration to retain old log files
        enqueue=True,  # Enqueue log messages
    )

    # Example log messages
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")
    logger.critical("This is a critical message")

Attributes:
    None

Todo:
    * Add support for additional logging handlers.
    * Implement asynchronous logging.

Author:
    Mike Ryan

Date Created:
    2021/07/16

Date Updated:
    2024/07/27

License:
    MIT
"""
import logging
import os
import shutil
from datetime import datetime, timedelta
from multiprocessing import Lock
from pathlib import Path
from uuid import uuid4

from loguru import logger

rotation_lock = Lock()

class SafeFileSink:
    """
    A class to handle safe file logging with rotation and retention policies.

    This class provides mechanisms to manage log files by rotating them based on size and retaining them for a specified duration. It also supports optional compression of log files.

    Attributes:
        path (str): The path to the log file.
        rotation_size (int): The size threshold for log rotation in bytes.
        retention_days (timedelta): The duration to retain old log files.
        compression (str, optional): The compression method to use for old log files.

    Methods:
        parse_size(size_str): Parses a size string (e.g., '100MB') and returns the size in bytes.
        parse_duration(duration_str): Parses a duration string (e.g., '7 days') and returns a timedelta object.

    Example:
        safe_file_sink = SafeFileSink(
            path='logs/app.log',
            rotation='100 MB',
            retention='30 days',
            compression='zip'
        )

        # This will set up a log file at 'logs/app.log' with rotation at 100 MB,
        # retention for 30 days, and compression using zip.
    """
    def __init__(self, path, rotation, retention, compression=None):
        self.path = path
        self.rotation_size = self.parse_size(rotation)
        self.retention_days = self.parse_duration(retention)
        self.compression = compression

    @staticmethod
    def parse_size(size_str): # pragma: no cover
        """
        Parses a size string and returns the size in bytes.

        Args:
            size_str (str): The size string (e.g., '100MB').

        Returns:
            int: The size in bytes.
        """
        size_str = size_str.upper()
        if size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        elif size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        else:
            return int(size_str)

    @staticmethod
    def parse_duration(duration_str): # pragma: no cover
        """
        Parses a duration string and returns a timedelta object.

        Args:
            duration_str (str): The duration string (e.g., '7 days').

        Returns:
            timedelta: The duration as a timedelta object.
        """
        duration_str = duration_str.lower()
        if 'day' in duration_str:
            return timedelta(days=int(duration_str.split()[0]))
        elif 'hour' in duration_str:
            return timedelta(hours=int(duration_str.split()[0]))
        elif 'minute' in duration_str:
            return timedelta(minutes=int(duration_str.split()[0]))
        else:
            return timedelta(days=0)

    def __call__(self, message): # pragma: no cover
        """
        Handles the logging of a message, including writing, rotating, and applying retention policies.

        Args:
            message (str): The log message to be written.

        This method ensures thread-safe logging by acquiring a lock before writing the message,
        rotating the logs if necessary, and applying the retention policy to remove old log files.
        """
        with rotation_lock:
            self.write_message(message)
            self.rotate_logs()
            self.apply_retention()

    def write_message(self, message): # pragma: no cover
        """
        Writes a log message to the log file.

        Args:
            message (str): The log message to be written.

        This method opens the log file in append mode and writes the message to it.
        """
        with open(self.path, 'a') as f:
            f.write(message)

    def rotate_logs(self): # pragma: no cover
        """
        Rotates the log file if it exceeds the specified rotation size.

        This method checks the size of the current log file. If the file size exceeds the specified rotation size, it renames the current log file by appending a timestamp to its name. Optionally, it compresses the rotated log file using the specified compression method and removes the original uncompressed file.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: If there is an error renaming or compressing the log file.
        """
        if os.path.getsize(self.path) >= self.rotation_size:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            rotated_path = f"{self.path}.{timestamp}"
            os.rename(self.path, rotated_path)
            if self.compression:
                shutil.make_archive(rotated_path, self.compression, root_dir=os.path.dirname(rotated_path), base_dir=os.path.basename(rotated_path))
                os.remove(rotated_path)

    def apply_retention(self): # pragma: no cover
        """
        Applies the retention policy to remove old log files.

        This method iterates through the log files in the directory of the current log file. It checks the modification time of each log file and removes those that are older than the specified retention period.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: If there is an error removing a log file.
        """
        now = datetime.now()
        for filename in os.listdir(os.path.dirname(self.path)):
            if filename.startswith(os.path.basename(self.path)) and len(filename.split('.')) > 1:
                file_path = os.path.join(os.path.dirname(self.path), filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_time > self.retention_days:
                    os.remove(file_path)

def config_log(
    logging_directory: str = "log",
    log_name: str = "log",
    logging_level: str = "INFO",
    log_rotation: str = "100 MB",
    log_retention: str = "30 days",
    log_backtrace: bool = False,
    log_format: str = None,
    log_serializer: bool = False,
    log_diagnose: bool = False,
    app_name: str = None,
    append_app_name: bool = False,
    enqueue: bool = True,
    intercept_standard_logging: bool = True,
    compression: str = 'zip',
):
    """
    Configures the logging settings for the application.

    This function sets up the logging configuration, including the log directory, log file name, logging level, log rotation, retention policies, and other optional settings.

    Args:
        logging_directory (str): The directory where log files will be stored. Defaults to "log".
        log_name (str): The base name of the log file. Defaults to "log".
        logging_level (str): The logging level (e.g., "INFO", "DEBUG"). Defaults to "INFO".
        log_rotation (str): The size threshold for log rotation (e.g., "100 MB"). Defaults to "100 MB".
        log_retention (str): The duration to retain old log files (e.g., "30 days"). Defaults to "30 days".
        log_backtrace (bool): Whether to include backtrace information in logs. Defaults to False.
        log_format (str, optional): The format string for log messages. Defaults to a predefined format if not provided.
        log_serializer (bool): Whether to serialize log messages. Defaults to False.
        log_diagnose (bool): Whether to include diagnostic information in logs. Defaults to False.
        app_name (str, optional): The name of the application. Defaults to None.
        append_app_name (bool): Whether to append the application name to the log file name. Defaults to False.
        enqueue (bool): Whether to enqueue log messages for asynchronous processing. Defaults to True.
        intercept_standard_logging (bool): Whether to intercept standard logging calls. Defaults to True.
        compression (str): The compression method for rotated log files (e.g., "zip"). Defaults to 'zip'.

    Returns:
        None

    Example:
        config_log(
            logging_directory='logs',
            log_name='app_log',
            logging_level='DEBUG',
            log_rotation='50 MB',
            log_retention='7 days',
            log_backtrace=True,
            log_format='{time} - {level} - {message}',
            log_serializer=True,
            log_diagnose=True,
            app_name='MyApp',
            append_app_name=True,
            enqueue=False,
            intercept_standard_logging=False,
            compression='gz'
        )

    This will configure the logging settings with the specified parameters, setting up a log file at 'logs/app_log' with rotation at 50 MB, retention for 7 days, and other specified options.
    """

    # If the log_name ends with ".log", remove the extension
    if log_name.endswith(".log"):
        log_name = log_name.replace(".log", "")  # pragma: no cover

    # If the log_name ends with ".json", remove the extension
    if log_name.endswith(".json"):
        log_name = log_name.replace(".json", "")  # pragma: no cover

    # Set default log format if not provided
    if log_format is None:  # pragma: no cover
        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSSSSS}</green> | <level>{level: <8}</level> | <cyan> {name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"  # pragma: no cover

    if log_serializer is True:
        log_format = "{message}"  # pragma: no cover
        log_name = f"{log_name}.json"  # pragma: no cover
    else:
        log_name = f"{log_name}.log"  # pragma: no cover

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
        log_format += " | app_name: {extra[app_name]}"

    # Remove any previously added sinks
    logger.remove()

    # Append app name to log file name if required
    if append_app_name is True and app_name is not None:
        log_name = log_name.replace(".", f"_{app_name}.")

    # Construct log file path
    log_path = Path.cwd().joinpath(logging_directory).joinpath(log_name)

    # Add loguru logger with specified configuration
    logger.add(
        SafeFileSink(log_path, rotation=log_rotation, retention=log_retention, compression=compression),
        level=logging_level.upper(),
        format=log_format,
        enqueue=enqueue,
        backtrace=log_backtrace,
        serialize=log_serializer,
        diagnose=log_diagnose,
    )

    basic_config_handlers: list = []

    class InterceptHandler(logging.Handler):
        """
        A logging handler that intercepts standard logging messages and redirects them to Loguru.

        This handler captures log messages from the standard logging module and forwards them to Loguru, preserving the log level and message details.

        Methods:
            emit(record):
                Emits a log record to Loguru.
        """

        def emit(self, record):
            """
            Emits a log record to Loguru.

            This method captures the log record, determines the appropriate Loguru log level, and logs the message using Loguru. It also handles exceptions and finds the caller's frame to maintain accurate log information.

            Args:
                record (logging.LogRecord): The log record to be emitted.

            Returns:
                None
            """
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

    if intercept_standard_logging:
        # Add interceptor handler to all existing loggers
        for name in logging.Logger.manager.loggerDict:
            logging.getLogger(name).addHandler(InterceptHandler())

        # Add interceptor handler to the root logger
        basic_config_handlers.append(InterceptHandler())

    # Set the root logger's level to the lowest level possible
    logging.getLogger().setLevel(logging.NOTSET)

    if intercept_standard_logging:
        # Append an InterceptHandler instance to the handlers list if intercept_standard_logging is True
        basic_config_handlers.append(InterceptHandler())

    if len(basic_config_handlers) > 0:
        logging.basicConfig(handlers=basic_config_handlers, level=logging_level.upper())
