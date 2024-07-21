# -*- coding: utf-8 -*-
"""
This module provides a comprehensive logging setup using the loguru library, facilitating easy logging management for Python applications. The `config_log` function, central to this module, allows for extensive customization of logging behavior. It supports specifying the logging directory, log file name, logging level, and controls for log rotation, retention, and formatting among other features. Additionally, it offers advanced options like backtrace and diagnose for in-depth debugging, and the ability to append the application name to the log file for clearer identification.

Usage example:

```python
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
```

Author: Mike Ryan
DateCreated: 2021/07/16
DateUpdated: 2024/07/24

License: MIT
"""
import time
import logging
from pathlib import Path
from uuid import uuid4

from loguru import logger


def config_log(
    logging_directory: str = 'log',
    log_name: str = 'log',
    logging_level: str = 'INFO',
    log_rotation: str = '100 MB',
    log_retention: str = '30 days',
    log_backtrace: bool = False,
    log_format: str = None,
    log_serializer: bool = False,
    log_diagnose: bool = False,
    app_name: str = None,
    append_app_name: bool = False,
    enqueue: bool = True,
    intercept_standard_logging: bool = True,
    file_sink: bool = True,
):
    """
    Configures and sets up a logger using the loguru package.

    Parameters:
    - logging_directory (str): The directory where logs will be stored. Default is "log".
    - log_name (str): The name of the log file. Default is "log" (extension automatically set in 0.12.2).
    - logging_level (str): The logging level. Default is "INFO".
    - log_rotation (str): The log rotation size. Default is "100 MB".
    - log_retention (str): The log retention period. Default is "30 days".
    - log_backtrace (bool): Whether to enable backtrace. Default is False.
    - log_format (str): The log format. Default is None.
    - log_serializer (bool): Whether to disable log serialization. Default is False.
    - log_diagnose (bool): Whether to enable diagnose. Default is False.
    - app_name (str): The application name. Default is None.
    - append_app_name (bool): Whether to append the application name to the log file name. Default is False.
    - enqueue (bool): Whether to enqueue log messages. Default is True.
    - intercept_standard_logging (bool): Whether to intercept standard logging. Default is True.
    - file_sink (bool): Whether to use a file sink. Default is True.

    Raises:
    - ValueError: If the provided logging level is not valid.

    Usage Example:
    ```python
    from logging_config import config_log

    config_log(
        logging_directory='logs',
        log_name='app.log',
        logging_level='DEBUG',
        log_rotation='100 MB',
        log_retention='10 days',
        log_backtrace=True,
        log_format="<green>{time:YYYY-MM-DD HH:mm:ss.SSSSSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        log_serializer=False,
        log_diagnose=True,
        app_name='my_app',
        append_app_name=True,
        enqueue=True,
        intercept_standard_logging=True,
        file_sink=True
    )
    ```
    """

    # If the log_name ends with ".log", remove the extension
    if log_name.endswith('.log'):
        log_name = log_name.replace('.log', '')  # pragma: no cover

    # If the log_name ends with ".json", remove the extension
    if log_name.endswith('.json'):
        log_name = log_name.replace('.json', '')  # pragma: no cover

    # Set default log format if not provided
    if log_format is None:  # pragma: no cover
        log_format = '<green>{time:YYYY-MM-DD HH:mm:ss.SSSSSS}</green> | <level>{level: <8}</level> | <cyan> {name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'  # pragma: no cover

    if log_serializer is True:
        log_format = '{message}'  # pragma: no cover
        log_name = f'{log_name}.json'  # pragma: no cover
    else:
        log_name = f'{log_name}.log'  # pragma: no cover

    # Validate logging level
    log_levels: list = ['DEBUG', 'INFO', 'ERROR', 'WARNING', 'CRITICAL']
    if logging_level.upper() not in log_levels:
        raise ValueError(f'Invalid logging level: {logging_level}. Valid levels are: {log_levels}')

    # Generate unique trace ID
    trace_id: str = str(uuid4())
    logger.configure(extra={'app_name': app_name, 'trace_id': trace_id})

    # Append app name to log format if provided
    if app_name is not None:
        log_format += ' | app_name: {extra[app_name]}'

    # Remove any previously added sinks
    logger.remove()

    # Append app name to log file name if required
    if append_app_name is True and app_name is not None:
        log_name = log_name.replace('.', f'_{app_name}.')

    # Construct log file path
    log_path = Path.cwd().joinpath(logging_directory).joinpath(log_name)

    # Add loguru logger with specified configuration
    logger.add(
        log_path,
        level=logging_level.upper(),
        format=log_format,
        enqueue=enqueue,
        backtrace=log_backtrace,
        rotation=log_rotation,
        retention=log_retention,
        compression='zip',
        serialize=log_serializer,
        diagnose=log_diagnose,
    )

    basic_config_handlers:list = []

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


    if intercept_standard_logging:
        # Add interceptor handler to all existing loggers
        for name in logging.root.manager.loggerDict:
            logging.getLogger(name).addHandler(InterceptHandler())

        # Add interceptor handler to the root logger
        basic_config_handlers.append(InterceptHandler())

    # Set the root logger's level to the lowest level possible
    logging.getLogger().setLevel(logging.NOTSET)


    class ResilientFileSink:
        """
        A file sink designed for resilience, capable of retrying write operations.

        This class implements a resilient file writing mechanism that attempts to write messages to a file, retrying the operation a specified number of times if it fails. This is particularly useful in scenarios where write operations might intermittently fail due to temporary issues such as file system locks or networked file system delays.

        Attributes:
            path (str): The path to the file where messages will be written.
            max_retries (int): The maximum number of retry attempts for a failed write operation.
            retry_delay (float): The delay between retry attempts, in seconds.

        Methods:
            write(message): Attempts to write a message to the file, retrying on failure up to `max_retries` times.
        """
        def __init__(self, path, max_retries=5, retry_delay=0.1):
            self.path = path
            self.max_retries = max_retries
            self.retry_delay = retry_delay

        def write(self, message): # pragma: no cover
            for attempt in range(self.max_retries):
                try:
                    with open(self.path, 'a') as file:
                        file.write(str(message))
                    break  # Successfully written, break the loop
                except FileNotFoundError:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)  # Wait before retrying
                    else:
                        raise  # Reraise if max retries exceeded


    if file_sink:
        # Create an instance of ResilientFileSink
        resilient_sink = ResilientFileSink(str(log_path))

        # Configure the logger to use the ResilientFileSink
        basic_config_handlers.append(resilient_sink)

    if intercept_standard_logging:
        basic_config_handlers.append(InterceptHandler())

    if len(basic_config_handlers) > 0:
        logging.basicConfig(handlers=basic_config_handlers, level=logging_level.upper())
