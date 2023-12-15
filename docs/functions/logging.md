# dsg_lib.common.logging_config

This module provides a convenient way to configure logging for your application using the `loguru` package. It includes an interceptor for standard Python logging and allows you to customize various aspects of logging.

## Function: config_log

The `config_log` function is used to configure and set up a logger.

### Parameters

- `logging_directory` (str, optional): Directory where logs will be stored. Default is "log".
- `log_name` (str, optional): Name of the log file. Default is "log.json".
- `logging_level` (str, optional): Logging level. Default is "INFO".
- `log_rotation` (str, optional): Log rotation size. Default is "10 MB".
- `log_retention` (str, optional): Log retention period. Default is "30 days".
- `log_backtrace` (bool, optional): Enable backtrace. Default is False.
- `log_format` (str, optional): Log format. Default is None.
- `log_serializer` (bool, optional): Enable log serialization. Default is False.
- `log_diagnose` (bool, optional): Enable diagnose. Default is False.
- `app_name` (str, optional): Application name. Default is None.
- `append_app_name` (bool, optional): Append application name to the log file name. Default is False.

### Usage

```python
from dsg_lib.common.logging_config import config_log

# Configure the logger
config_log(
    logging_directory='logs',  # Directory where logs will be stored
    log_name='app.log',  # Name of the log file
    logging_level='DEBUG',  # Logging level
    log_rotation='500 MB',  # Log rotation size
    log_retention='10 days',  # Log retention period
    log_backtrace=True,  # Enable backtrace
    log_format="<green>{time:YYYY-MM-DD HH:mm:ss.SSSSSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",  # Log format
    log_serializer=False,  # Disable log serialization
    log_diagnose=True,  # Enable diagnose
    app_name='my_app',  # Application name
    append_app_name=True  # Append application name to the log file name
)

# Now you can use the logger in your application
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.error("This is an error message")
```

This will configure the logger to log all messages with level DEBUG or higher to a file named 'app.log' in the 'logs' directory. The log file will be rotated when it reaches a size of 500 MB and logs older than 10 days will be deleted. The log format is customized and the application name is appended to the log file name.